import requests
import time
import os
from dotenv import load_dotenv

# 1. Загрузить .env
load_dotenv()

GOLOGIN_TOKEN = os.getenv("GOLOGIN_TOKEN")
GOLOGIN_API = "https://api.gologin.com"

if not GOLOGIN_TOKEN:
    raise RuntimeError("GOLOGIN_TOKEN is not set in environment (.env)")

def create_profile(proxy=None, navigator=None):
    headers = {
        "Authorization": f"Bearer {GOLOGIN_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "name": "lastuser-profile",
        "os": "win",
        "browserType": "chrome",
        "navigator": navigator or {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "language": "en-US,en;q=0.9",
            "resolution": "1920x1080",
            "platform": "Win32",
        },
        "proxy": proxy or {"mode": "none"},
    }
    resp = requests.post(f"{GOLOGIN_API}/browser", json=payload, headers=headers)
    print("GoLogin create_profile payload:", payload)
    print("GoLogin create_profile response:", resp.status_code, resp.text)
    try:
        resp.raise_for_status()
    except Exception as ex:
        print(f"Ошибка создания профиля: {resp.status_code} {resp.text}")
        raise
    return resp.json()["id"]

def start_profile(profile_id):
    headers = {"Authorization": f"Bearer {GOLOGIN_TOKEN}"}
    url = f"{GOLOGIN_API}/browser/{profile_id}/start?automation=true"
    resp = requests.get(url, headers=headers)
    print("GoLogin start_profile response:", resp.status_code, resp.text)
    try:
        resp.raise_for_status()
    except Exception as ex:
        print(f"Ошибка запуска профиля: {resp.status_code} {resp.text}")
        raise
    ws_url = resp.json().get("wsEndpoint") or resp.json().get("wsUrl")
    if not ws_url:
        raise RuntimeError("No wsEndpoint in GoLogin response! Ответ: " + resp.text)
    time.sleep(3)
    return ws_url

def stop_profile(profile_id):
    headers = {"Authorization": f"Bearer {GOLOGIN_TOKEN}"}
    try:
        resp = requests.get(f"{GOLOGIN_API}/browser/{profile_id}/stop", headers=headers)
        print("GoLogin stop_profile response:", resp.status_code, resp.text)
    except Exception as e:
        print(f"Error stopping GoLogin profile: {e}")
