from aiogram import Router, types
from ai import ai_answer
from database import db_connect

router = Router()

@router.message(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Я умный бот с ИИ и VIP системой.")

@router.message()
async def ai_chat(message: types.Message):
    answer = await ai_answer(message.text)
    await message.answer(answer)