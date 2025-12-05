from fastapi import FastAPI, Request
from aiogram.types import Update
from aiogram import Bot
from aiogram import Dispatcher

from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH
from bot import dp, bot   # твой dp из bot.py
from db import init_db

app = FastAPI()

@app.on_event("startup")
async def startup():
    print("Инициализация базы...")
    await init_db()

    print("Установка вебхука...")
    await bot.set_webhook(WEBHOOK_URL)

    print("Webhook установлен!")

@app.post(WEBHOOK_PATH)
async def webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def home():
    return {"status": "running"}