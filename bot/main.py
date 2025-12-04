import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from config import BOT_TOKEN
from ai import ai_answer
from db import init_db

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer("Бот работает! Напиши мне сообщение.")


@dp.message(F.text)
async def handle_message(message: Message):
    user_text = message.text
    ai_response = await ai_answer(user_text)
    await message.answer(ai_response)


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())