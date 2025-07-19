import requests
import time
import os
from dotenv import load_dotenv
import os

GOLOGIN_TOKEN = os.getenv("GOLOGIN_TOKEN")  # Токен берём из переменных окружения
GOLOGIN_API = "https://api.gologin.com"

# Теперь GOLOGIN_TOKEN будет читаться из .env автоматически!
print("GOLOGIN_TOKEN:", GOLOGIN_TOKEN)  # для проверки, можно удалить

def create_profile(proxy=None, user_agent=None):
    headers = {"Authorization": f"Bearer {GOLOGIN_TOKEN}"}
    payload = {
        "name": "lastuser-profile",
        "os": "win",
        "navigator": {"userAgent": user_agent or ""},
    }
    if proxy:
        payload["proxy"] = {
            "mode": "http",
            "host": proxy["ip"],
            "port": proxy["port"],
            "username": proxy.get("login", ""),
            "password": proxy.get("password", ""),
        }
    resp = requests.post(f"{GOLOGIN_API}/browser", json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()["id"]

def start_profile(profile_id):
    headers = {"Authorization": f"Bearer {GOLOGIN_TOKEN}"}
    resp = requests.get(f"{GOLOGIN_API}/browser/{profile_id}/start", headers=headers)
    resp.raise_for_status()
    # Ждём пока профиль запустится, потом получаем wsEndpoint
    ws_url = resp.json().get("wsEndpoint")
    # ws_url пригодится для Playwright/Puppeteer
    time.sleep(3)
    return ws_url

def stop_profile(profile_id):
    headers = {"Authorization": f"Bearer {GOLOGIN_TOKEN}"}
    requests.get(f"{GOLOGIN_API}/browser/{profile_id}/stop", headers=headers)
