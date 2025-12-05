from fastapi import FastAPI, Request
from aiogram.types import Update
from bot import dp, bot
from db import init_db

app = FastAPI()

@app.on_event("startup")
async def startup():
    print("▶ STARTUP BEGIN")
    await init_db()
    print("▶ DB INITIALIZED")

    WEBHOOK_URL = "https://ТВОЙ-САЙТ-RENDER.onrender.com/webhook"
    await bot.set_webhook(WEBHOOK_URL)
    print("▶ WEBHOOK SET:", WEBHOOK_URL)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def home():
    return {"running": True}