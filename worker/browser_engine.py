from playwright.sync_api import sync_playwright
import random, time
from worker.antidetect_gologin import create_profile, start_profile, stop_profile

def random_user_agent():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)..."
    ]
    return random.choice(agents)

async def run_scenario(job):
    # Пример с прокси и антидетектом
    proxy = None
    user_agent = random_user_agent()
    profile_id = create_profile(proxy=proxy, user_agent=user_agent)
    ws_url = start_profile(profile_id)
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(ws_url)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()
            page.goto("https://yandex.ru/")
            # Имитация поведения
            for char in job.campaign.query:
                page.locator('input[name="text"]').type(char)
                time.sleep(random.uniform(0.07, 0.21))
            page.keyboard.press("Enter")
            time.sleep(random.uniform(2, 3.5))
            links = page.query_selector_all('a.link_theme_normal')
            for link in links:
                href = link.get_attribute('href')
                if href and job.campaign.url in href:
                    link.click()
                    break
            # Человеческие паттерны: скроллинг, клики, задержки
            for _ in range(random.randint(3, 12)):
                x = random.randint(100, 1100)
                y = random.randint(120, 900)
                page.mouse.move(x, y, steps=random.randint(8, 20))
                page.mouse.wheel(0, random.randint(100, 800))
                time.sleep(random.uniform(0.4, 2.2))
            # Поведение по сценарию (например, заполнить форму)
            if job.campaign.config and "fill_form" in job.campaign.config.get("scenario", []):
                if page.query_selector("form input"):
                    page.fill("form input", "lastuser test")
                    time.sleep(random.uniform(1, 3))
            time.sleep(random.uniform(22, 90))
            browser.close()
    finally:
        stop_profile(profile_id)


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

async def run_scenario(job):
    profile_id = create_profile(proxy=None)
    ws_url = start_profile(profile_id)
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(ws_url)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()
            page.goto("https://yandex.ru/")
            for char in job.campaign.query:
                page.locator('input[name="text"]').type(char)
                time.sleep(rand_t(0.07, 0.21))
            page.keyboard.press("Enter")
            time.sleep(rand_t(2, 3.5))
            # Поиск нужного сайта
            links = page.query_selector_all('a.link_theme_normal')
            for link in links:
                href = link.get_attribute('href')
                if href and job.campaign.url in href:
                    link.click()
                    break
            # Динамический сценарий из job.campaign.config["scenario"]
            scenario = (job.campaign.config or {}).get("scenario", [])
            for action in scenario:
                result = do_action(page, action)
                if result == "exit":
                    break
            time.sleep(rand_t(3, 8))
            browser.close()
    finally:
        stop_profile(profile_id)
