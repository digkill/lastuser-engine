import os
import asyncio
import requests
import logging
from playwright.async_api import async_playwright

GOLOGIN_TOKEN = os.getenv("GOLOGIN_TOKEN")
GOLOGIN_API = "https://api.gologin.com"

logger = logging.getLogger("browser")
logging.basicConfig(level=logging.INFO)

# ========== GoLogin API ==========

def create_gologin_profile(proxy: dict = None, notes="lastuser") -> str:
    headers = {"Authorization": f"Bearer {GOLOGIN_TOKEN}", "Content-Type": "application/json"}
    data = {
        "name": notes,
        "os": "win",
        "navigator": {"language": "en-US,en;q=0.9"},
        "proxy": proxy or {},
    }
    resp = requests.post(f"{GOLOGIN_API}/browser", headers=headers, json=data, timeout=15)
    resp.raise_for_status()
    return resp.json()["id"]

def start_gologin_profile(profile_id: str) -> str:
    headers = {"Authorization": f"Bearer {GOLOGIN_TOKEN}"}
    resp = requests.get(f"{GOLOGIN_API}/browser/{profile_id}/start?automation=true", headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()["wsUrl"]

def stop_gologin_profile(profile_id: str):
    headers = {"Authorization": f"Bearer {GOLOGIN_TOKEN}"}
    try:
        requests.get(f"{GOLOGIN_API}/browser/{profile_id}/stop", headers=headers, timeout=10)
    except Exception as e:
        logger.warning(f"Can't stop profile {profile_id}: {e}")

# ========== Основная функция для воркера ==========

async def run_browser_task(
    url: str,
    actions: list = None,
    use_gologin: bool = True,
    gologin_profile_id: str = None,
    proxy: dict = None
):
    """
    Выполняет сценарий для одного задания.
    - url: адрес сайта
    - actions: список действий, например [{"type": "click", ...}]
    - use_gologin: использовать GoLogin
    - gologin_profile_id: опционально, для реюза профиля
    - proxy: настройки прокси
    """
    ws_url = None
    created_profile = False
    profile_id = None

    if use_gologin:
        if not gologin_profile_id:
            profile_id = create_gologin_profile(proxy=proxy)
            logger.info(f"Created GoLogin profile: {profile_id}")
            created_profile = True
        else:
            profile_id = gologin_profile_id

        ws_url = start_gologin_profile(profile_id)
        logger.info(f"Started GoLogin browser for profile {profile_id}")
    else:
        profile_id = None

    try:
        async with async_playwright() as pw:
            if ws_url:
                browser = await pw.chromium.connect_over_cdp(ws_url)
                context = await browser.new_context()
            else:
                browser = await pw.chromium.launch(headless=True)
                context = await browser.new_context()

            page = await context.new_page()
            await page.goto(url, timeout=40000)

            # Выполнение сценария
            if actions:
                for action in actions:
                    try:
                        if action["type"] == "click":
                            await page.click(action["selector"], timeout=10000)
                        elif action["type"] == "input":
                            await page.fill(action["selector"], action["text"])
                        elif action["type"] == "wait":
                            await asyncio.sleep(action.get("seconds", 1))
                        # Можно расширить новыми типами действий
                    except Exception as ex:
                        logger.warning(f"Action failed: {action}, error: {ex}")

            html = await page.content()
            # Можно добавить: сохранение скриншота, cookies и пр.

            await context.close()
            await browser.close()
            return {
                "html": html,
                "profile_id": profile_id,
            }

    finally:
        if use_gologin and created_profile and profile_id:
            stop_gologin_profile(profile_id)
            logger.info(f"Stopped and removed GoLogin profile {profile_id}")

# ===== Пример использования из воркера =====
# result = await run_browser_task(
#     url=task.url,
#     actions=task.actions,
#     use_gologin=True,
#     proxy=task.proxy
# )
