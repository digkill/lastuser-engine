from aiogram import Bot, Dispatcher, types, executor
import os

TOKEN = os.getenv("TG_BOT_TOKEN", "your-token-here")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start", "status"])
async def status_cmd(message: types.Message):
    await message.answer("LastUser Engine Online!\n(Здесь будут статусы и алерты по задачам)")

if __name__ == "__main__":
    executor.start_polling(dp)
