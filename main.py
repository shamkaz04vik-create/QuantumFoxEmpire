from fastapi import FastAPI, Request
from aiogram import Bot
from aiogram.types import Update

from config import BOT_TOKEN, WEBHOOK_URL
from db import init_db
from bot.main import dp  # тут хендлеры

app = FastAPI()
bot = Bot(token=BOT_TOKEN)

# ==============================
# Установка Webhook при запуске
# ==============================
@app.on_event("startup")
async def on_startup():
    await init_db()
    await bot.set_webhook(WEBHOOK_URL)
    print("Webhook установлен:", WEBHOOK_URL)

# ==============================
# Обработка входящих обновлений Telegram
# ==============================
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

# ==============================
# Root endpoint
# ==============================
@app.get("/")
async def home():
    return {"status": "running", "webhook": WEBHOOK_URL}