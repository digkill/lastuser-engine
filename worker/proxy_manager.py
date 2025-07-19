import os
from aiogram import Bot, Dispatcher, types, executor

TOKEN = os.getenv("TG_BOT_TOKEN", "your-token-here")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Симуляция статусов (лучше интегрировать с FastAPI/Broker)
CAMPAIGNS = {"1": "In progress", "2": "Completed", "3": "Failed"}

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("👋 Привет! Это LastUser Engine Telegram-бот.\n\nДоступные команды:\n/status — статус кампаний\n/job <id> — статус задачи\n/retry <id> — повторить задачу")

@dp.message_handler(commands=["status"])
async def status_cmd(message: types.Message):
    txt = "\n".join([f"Кампания {cid}: {st}" for cid, st in CAMPAIGNS.items()])
    await message.answer(f"Статусы кампаний:\n{txt}")

@dp.message_handler(lambda m: m.text.startswith("/job"))
async def job_cmd(message: types.Message):
    job_id = message.text.split(" ")[-1]
    # Имитация (реально — делаем запрос в backend)
    await message.answer(f"Статус задачи {job_id}: done (пример)")

@dp.message_handler(lambda m: m.text.startswith("/retry"))
async def retry_cmd(message: types.Message):
    job_id = message.text.split(" ")[-1]
    await message.answer(f"Задача {job_id} поставлена на повтор")

if __name__ == "__main__":
    executor.start_polling(dp)
