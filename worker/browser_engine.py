import base64
import datetime
import os
import random
import time
from playwright.sync_api import sync_playwright
import psycopg2
from antidetect_gologin import create_profile, start_profile, stop_profile

def save_worker_log(
    worker_id, url, action_type, action_data,
    status, screenshot_bytes=None, error_msg=None,
    started_at=None, finished_at=None
):
    duration = int((finished_at - started_at).total_seconds() * 1000)
    screenshot_b64 = None
    if screenshot_bytes:
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO worker_logs
                (worker_id, url, action_type, action_data, status, screenshot, error_msg, started_at, finished_at, duration_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    worker_id, url, action_type, action_data, status,
                    screenshot_b64, error_msg,
                    started_at, finished_at, duration
                )
            )
    conn.close()

def rand_t(min_, max_):
    return random.uniform(min_, max_)

def do_action(page, action):
    if action["action"] == "wait":
        time.sleep(rand_t(action.get("min",1), action.get("max",2)))
    elif action["action"] == "scroll":
        for _ in range(action.get("times",1)):
            page.mouse.wheel(0, random.randint(200, 800))
            time.sleep(rand_t(action.get("pause_min",0.3), action.get("pause_max",1.0)))
    elif action["action"] == "random_click" and random.random() < action.get("prob", 0.2):
        links = page.query_selector_all("a")
        if links:
            random.choice(links).click()
            time.sleep(rand_t(0.5, 2))
    elif action["action"] == "ad_click" and random.random() < action.get("prob", 0.08):
        ads = page.query_selector_all('.serp-item--ad')
        if ads:
            random.choice(ads).click()
            time.sleep(rand_t(3, 9))
    elif action["action"] == "fill_form" and random.random() < action.get("prob", 0.1):
        for field, value in action.get("fields", {}).items():
            if page.query_selector(f"input[name={field}]"):
                page.fill(f"input[name={field}]", value)
        submit = page.query_selector("form button[type=submit]")
        if submit:
            submit.click()
            time.sleep(rand_t(2, 4))
    elif action["action"] == "read":
        time.sleep(rand_t(action.get("min", 5), action.get("max", 20)))
    elif action["action"] == "bounce" and random.random() < action.get("prob", 0.05):
        page.go_back()
        time.sleep(rand_t(0.5, 1.7))
        return "exit"
    return "continue"

def run_scenario(job, fingerprint=None):
    # 1. Формируем fingerprint для GoLogin
    navigator = None
    if fingerprint:
        try:
            navigator = {
                "userAgent": fingerprint.get("userAgent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"),
                "language": fingerprint.get("languages", [["en-US"]])[0][0] if fingerprint.get("languages") else "en-US",
                "resolution": "x".join([str(x) for x in fingerprint.get("screenResolution", [1920, 1080])]),
                "platform": fingerprint.get("platform", "Win32"),
            }
        except Exception as ex:
            print("Ошибка парсинга fingerprint:", ex)
            navigator = None

    # 2. Создаем профайл GoLogin с нужным fingerprint
    profile_id = create_profile(proxy=None, navigator=navigator)
    ws_url = start_profile(profile_id)

    started = datetime.datetime.utcnow()
    status = "success"
    error_msg = ""
    screenshot_bytes = None
    action_log = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(ws_url)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()

            # (Опционально) патчим JS-финты
            if navigator:
                js_patch = f"""
                    Object.defineProperty(navigator, 'platform', {{get: () => '{navigator["platform"]}'}});
                    Object.defineProperty(navigator, 'userAgent', {{get: () => '{navigator["userAgent"]}'}});
                    Object.defineProperty(navigator, 'languages', {{get: () => ['{navigator["language"]}']}});
                """
                page.add_init_script(js_patch)

            try:
                page.goto("https://yandex.ru/")
                action_log.append({"step": "goto", "url": "https://yandex.ru/", "ts": str(datetime.datetime.utcnow())})

                for char in job.campaign.query:
                    page.locator('input[name="text"]').type(char)
                    time.sleep(rand_t(0.07, 0.21))
                page.keyboard.press("Enter")
                time.sleep(rand_t(2, 3.5))
                action_log.append({"step": "search", "query": job.campaign.query, "ts": str(datetime.datetime.utcnow())})

                links = page.query_selector_all('a.link_theme_normal')
                found = False
                for link in links:
                    href = link.get_attribute('href')
                    if href and job.campaign.url in href:
                        link.click()
                        found = True
                        action_log.append({"step": "click_link", "href": href, "ts": str(datetime.datetime.utcnow())})
                        break
                if not found:
                    action_log.append({"step": "link_not_found", "ts": str(datetime.datetime.utcnow())})

                scenario = (job.campaign.config or {}).get("scenario", [])
                for action in scenario:
                    result = do_action(page, action)
                    action_log.append({"step": "scenario", "action": action, "result": result, "ts": str(datetime.datetime.utcnow())})
                    if result == "exit":
                        break

                time.sleep(rand_t(3, 8))
                screenshot_bytes = page.screenshot(full_page=True)
                action_log.append({"step": "screenshot", "ts": str(datetime.datetime.utcnow())})

            except Exception as ex:
                status = "fail"
                error_msg = str(ex)
                try:
                    screenshot_bytes = page.screenshot(full_page=True)
                except Exception:
                    screenshot_bytes = None
                action_log.append({"step": "exception", "error": error_msg, "ts": str(datetime.datetime.utcnow())})
                raise
            finally:
                browser.close()

    except Exception as ex:
        if not error_msg:
            status = "fail"
            error_msg = str(ex)
        if not screenshot_bytes:
            screenshot_bytes = None

    finally:
        finished = datetime.datetime.utcnow()
        save_worker_log(
            worker_id=profile_id,
            url=ws_url,
            action_type="site-crawl",
            action_data={"actions": action_log},
            status=status,
            screenshot_bytes=screenshot_bytes,
            error_msg=error_msg,
            started_at=started,
            finished_at=finished
        )
        stop_profile(profile_id)
