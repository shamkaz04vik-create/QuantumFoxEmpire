from fastapi import FastAPI, Request
from aiogram.types import Update
from aiogram import Bot

from config import BOT_TOKEN, WEBHOOK_URL
from bot import dp, bot
from db import init_db

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db()
    await bot.set_webhook(WEBHOOK_URL)
    print("Webhook установлен!")

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def home():
    return {"status": "running"}
    
    if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 10000))
    print(f"Starting server on port {port}")
    web.run_app(app, host="0.0.0.0", port=port)