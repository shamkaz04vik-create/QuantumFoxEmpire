# main.py
import os
from fastapi import FastAPI, Request
from aiogram.types import Update
from bot import dp, bot
from db import init_db, close_db
from config import WEBHOOK_URL

app = FastAPI()

@app.on_event("startup")
async def startup():
    print("▶ INIT DB")
    await init_db()
    print("▶ DB OK")
    # Устанавливаем webhook у Telegram (конечная точка /webhook)
    await bot.set_webhook(WEBHOOK_URL)
    print("▶ WEBHOOK OK:", WEBHOOK_URL)

@app.on_event("shutdown")
async def shutdown():
    print("▶ SHUTDOWN")
    await bot.delete_webhook()
    await close_db()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def home():
    return {"running": True}