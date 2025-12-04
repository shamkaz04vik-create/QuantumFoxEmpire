from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os

TOKEN = os.getenv("BOT_TOKEN") or "ТВОЙ_ТОКЕН"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Бот работает!")