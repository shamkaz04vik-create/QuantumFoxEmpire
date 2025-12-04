from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
import asyncio

from config import BOT_TOKEN, WEBHOOK_URL
from db import init_db
from bot.main import dp  # твой бот с хендлерами

app = FastAPI()
bot = Bot(token=BOT_TOKEN)

# ==============================
# Установка WEBHOOK
# ==============================
@app.on_event("startup")
async def on_startup():
    await init_db()
    await bot.set_webhook(WEBHOOK_URL)
    print("Webhook установлен:", WEBHOOK_URL)


# ==============================
# Получение обновлений от Telegram
# ==============================
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}


# ==============================
# Проверка состояния
# ==============================
@app.get("/")
async def home():
    return {"status": "running", "webhook": WEBHOOK_URL}