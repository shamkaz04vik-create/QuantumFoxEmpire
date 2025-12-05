# main.py — FastAPI приложение для Render (entrypoint: uvicorn main:app ...)
from fastapi import FastAPI, Request
from aiogram.types import Update
from aiogram import Bot
import os

from config import BOT_TOKEN, WEBHOOK_URL
from bot import dp, bot  # импортируем dp и bot из bot.py
from db import init_db

app = FastAPI()

@app.on_event("startup")
async def startup():
    print("▶ INIT DB")
    await init_db()  # обязательно инициализация БД
    print("▶ DB OK")
    # Устанавливаем webhook (можно пропустить, если уже поставлен вручную)
    try:
        await bot.set_webhook(WEBHOOK_URL)
        print("▶ WEBHOOK OK:", WEBHOOK_URL)
    except Exception as e:
        print("! ошибка установки webhook:", e)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    # feed_update — безопасно принимает апдейт
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "running"}