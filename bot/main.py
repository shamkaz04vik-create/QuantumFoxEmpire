from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from config import BOT_TOKEN
from ai import ai_answer
from db import add_user, log_message

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: Message):
    await add_user(message.from_user.id, message.from_user.username)
    await message.answer("Привет! Я умный чат-бот. Напиши сообщение 👇")

@dp.message(F.text)
async def ai_chat(message: Message):
    text = message.text
    answer = await ai_answer(text)

    await log_message(message.from_user.id, text, answer)
    await message.answer(answer)