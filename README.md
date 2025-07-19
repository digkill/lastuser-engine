# LastUser Engine

## Как запустить

1. Склонировать репозиторий и установить Playwright браузеры:
    ```
    pip install -r requirements.txt
    playwright install
    ```

2. Поднять всё через Docker Compose:
    ```
    docker-compose up --build
    ```

3. Открыть FastAPI backend: http://localhost:8000/docs
4. Запустить телеграм-бота из папки telegram_bot:
    ```
    python bot.py
    ```

## Как создать кампанию

POST /api/campaigns/  
Пример JSON:
```json
{
  "query": "купить iphone 15 москва",
  "url": "your-site.ru",
  "sessions": 10
}
```