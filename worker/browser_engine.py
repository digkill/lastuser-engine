import base64
import datetime
import os
import random
import time
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from playwright.async_api import async_playwright
from shared.db.session import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def save_worker_log(
        db: AsyncSession,
        worker_id, url, action_type, action_data,
        status, screenshot_bytes=None, error_msg=None,
        started_at=None, finished_at=None
):
    logger.info(f"Saving worker log for worker_id: {worker_id}")
    duration = int((finished_at - started_at).total_seconds() * 1000) if started_at and finished_at else 0
    screenshot_b64 = None
    if screenshot_bytes:
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')

    try:
        await db.execute(
            text(
                """
                INSERT INTO worker_logs
                (worker_id, url, action_type, action_data, status, screenshot, error_msg, started_at, finished_at, duration_ms)
                VALUES (:worker_id, :url, :action_type, :action_data, :status, :screenshot, :error_msg, :started_at, :finished_at, :duration)
                """
            ),
            {
                "worker_id": worker_id,
                "url": url,
                "action_type": action_type,
                "action_data": json.dumps(action_data, ensure_ascii=False),
                "status": status,
                "screenshot": screenshot_b64,
                "error_msg": error_msg,
                "started_at": started_at,
                "finished_at": finished_at,
                "duration": duration
            }
        )
        await db.commit()
        logger.info(f"Successfully saved worker log for worker_id: {worker_id}")
    except Exception as e:
        logger.error(f"Error saving worker log for worker_id {worker_id}: {e}")
        await db.rollback()


def rand_t(min_, max_):
    return random.uniform(min_, max_)


async def do_action(page, action):
    try:
        if action["action"] == "wait":
            await page.wait_for_timeout(int(rand_t(action.get("min", 1), action.get("max", 2)) * 1000))
        elif action["action"] == "scroll":
            for _ in range(action.get("times", 1)):
                await page.mouse.wheel(0, random.randint(200, 800))
                await page.wait_for_timeout(
                    int(rand_t(action.get("pause_min", 0.3), action.get("pause_max", 1.0)) * 1000))
        elif action["action"] == "random_click" and random.random() < action.get("prob", 0.2):
            links = await page.query_selector_all("a")
            if links:
                await random.choice(links).click()
                await page.wait_for_timeout(int(rand_t(0.5, 2) * 1000))
        elif action["action"] == "ad_click" and random.random() < action.get("prob", 0.08):
            ads = await page.query_selector_all('.serp-item--ad')
            if ads:
                await random.choice(ads).click()
                await page.wait_for_timeout(int(rand_t(3, 9) * 1000))
        elif action["action"] == "fill_form" and random.random() < action.get("prob", 0.1):
            for field, value in action.get("fields", {}).items():
                if await page.query_selector(f"input[name={field}]"):
                    await page.fill(f"input[name={field}]", value)
            submit = await page.query_selector("form button[type=submit]")
            if submit:
                await submit.click()
                await page.wait_for_timeout(int(rand_t(2, 4) * 1000))
        elif action["action"] == "read":
            await page.wait_for_timeout(int(rand_t(action.get("min", 5), action.get("max", 20)) * 1000))
        elif action["action"] == "bounce" and random.random() < action.get("prob", 0.05):
            await page.go_back()
            await page.wait_for_timeout(int(rand_t(0.5, 1.7) * 1000))
            return "exit"
        return "continue"
    except Exception as e:
        logger.error(f"Error performing action {action}: {e}")
        return "continue"


def prepare_navigator_from_fingerprint(fingerprint):
    if not fingerprint or not fingerprint.data:
        logger.warning("No fingerprint or fingerprint.data provided")
        return None
    try:
        fingerprint_data = fingerprint.data
        language = "en-US"
        langs = fingerprint_data.get("languages")
        if langs and isinstance(langs, list):
            if isinstance(langs[0], list):
                language = langs[0][0]
            elif isinstance(langs[0], str):
                language = langs[0]
        screen_resolution = fingerprint_data.get("screenResolution", [1920, 1080])
        if isinstance(screen_resolution, dict) and "value" in screen_resolution:
            screen_resolution = screen_resolution.get("value", [1920, 1080])
        if isinstance(screen_resolution, str):
            try:
                screen_resolution = json.loads(screen_resolution)
            except json.JSONDecodeError:
                logger.warning(f"Invalid screenResolution format: {screen_resolution}, using default [1920, 1080]")
                screen_resolution = [1920, 1080]
        if not isinstance(screen_resolution, list) or len(screen_resolution) < 2:
            logger.warning(f"Invalid screenResolution format: {screen_resolution}, using default [1920, 1080]")
            screen_resolution = [1920, 1080]
        navigator = {
            "user_agent": fingerprint_data.get("userAgent",
                                               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"),
            "accept_language": language,
            "viewport": {
                "width": int(screen_resolution[0]),
                "height": int(screen_resolution[1])
            },
            "platform": fingerprint_data.get("platform", "Win32"),
        }
        return navigator
    except Exception as ex:
        logger.error(f"Error parsing fingerprint.data: {ex}")
        return None


async def run_scenario(job, fingerprint=None, db: AsyncSession = None):
    if db is None:
        logger.error("Database session not provided to run_scenario")
        return
    logger.info(f"Starting run_scenario for job {job.id}")
    navigator = prepare_navigator_from_fingerprint(fingerprint) if fingerprint else None
    worker_id = f"job_{job.id}_{int(time.time())}"
    started = datetime.datetime.utcnow()
    status = "success"
    error_msg = ""
    screenshot_bytes = None
    action_log = []

    try:
        logger.info(f"Starting Playwright for job {job.id}")
        async with async_playwright() as p:
            browser_args = {
                "headless": True,
                "args": ["--disable-blink-features=AutomationControlled"],
            }
            logger.info(f"Launching browser with args: {browser_args}")
            browser = await p.chromium.launch(**browser_args)

            context_args = {
                "no_viewport": False,
            }
            if navigator:
                context_args.update({
                    "user_agent": navigator["user_agent"],
                    "locale": navigator["accept_language"],
                    "viewport": navigator["viewport"],
                })
            logger.info(f"Creating new context with args: {context_args}")
            context = await browser.new_context(**context_args)

            if navigator:
                js_patch = f"""
                    Object.defineProperty(navigator, 'platform', {{get: () => '{navigator["platform"]}'}});
                    Object.defineProperty(navigator, 'userAgent', {{get: () => '{navigator["user_agent"]}'}});
                    Object.defineProperty(navigator, 'languages', {{get: () => ['{navigator["accept_language"]}']}});
                """
                await context.add_init_script(script=js_patch)

            page = await context.new_page()

            try:
                await page.goto("https://yandex.ru/")
                action_log.append({"step": "goto", "url": "https://yandex.ru/", "ts": str(datetime.datetime.utcnow())})

                for char in job.campaign.query:
                    await page.locator('input[id="text"]').type(char, delay=rand_t(70, 210))
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(int(rand_t(2, 3.5) * 1000))
                action_log.append(
                    {"step": "search", "query": job.campaign.query, "ts": str(datetime.datetime.utcnow())})

                links = await page.query_selector_all('a.link_theme_normal')
                found = False
                for link in links:
                    href = await link.get_attribute('href')
                    if href and job.campaign.url in href:
                        await link.click()
                        found = True
                        action_log.append({"step": "click_link", "href": href, "ts": str(datetime.datetime.utcnow())})
                        break
                if not found:
                    action_log.append({"step": "link_not_found", "ts": str(datetime.datetime.utcnow())})

                scenario = (job.campaign.config or {}).get("scenario", [])
                for action in scenario:
                    result = await do_action(page, action)
                    action_log.append(
                        {"step": "scenario", "action": action, "result": result, "ts": str(datetime.datetime.utcnow())})
                    if result == "exit":
                        break

                await page.wait_for_timeout(int(rand_t(3, 8) * 1000))
                screenshot_bytes = await page.screenshot(full_page=True)
                action_log.append({"step": "screenshot", "ts": str(datetime.datetime.utcnow())})

            except Exception as ex:
                status = "fail"
                error_msg = str(ex)
                try:
                    screenshot_bytes = await page.screenshot(full_page=True)
                except Exception:
                    screenshot_bytes = None
                action_log.append({"step": "exception", "error": error_msg, "ts": str(datetime.datetime.utcnow())})
            finally:
                await browser.close()
                logger.info(f"Browser closed for job {job.id}")

    except Exception as ex:
        status = "fail"
        error_msg = str(ex)
        logger.error(f"Error running Playwright for job {job.id}: {ex}")
        if not screenshot_bytes:
            screenshot_bytes = None

    finally:
        finished = datetime.datetime.utcnow()
        logger.info(f"Saving worker log and updating job status for job {job.id}")
        await save_worker_log(
            db=db,
            worker_id=worker_id,
            url="https://yandex.ru/",
            action_type="site-crawl",
            action_data={"actions": action_log},
            status=status,
            screenshot_bytes=screenshot_bytes,
            error_msg=error_msg,
            started_at=started,
            finished_at=finished
        )
        # Обновляем статус задания в таблице jobs
        try:
            logger.info(f"Updating job {job.id} status to {status}")
            await db.execute(
                text(
                    """
                    UPDATE jobs
                    SET status = :status,
                        worker_id = :worker_id,
                        started_at = :started_at,
                        finished_at = :finished_at,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :job_id
                    """
                ),
                {
                    "status": status,
                    "worker_id": worker_id,
                    "started_at": started,
                    "finished_at": finished,
                    "job_id": job.id
                }
            )
            await db.commit()
            logger.info(f"Successfully updated job {job.id} status to {status}")
        except Exception as e:
            logger.error(f"Error updating job {job.id} status: {e}")
            await db.rollback()