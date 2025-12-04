import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from fastapi import FastAPI, Request
import uvicorn

from bot import dp, bot  # импорт твоего бота

app = FastAPI()

WEBHOOK_URL = "https://quantumfoxempire.onrender.com/webhook"


@app.on_event("startup")
async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    print("🚀 Webhook установлен!")


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}


@app.get("/")
async def home():
    return {"status": "Bot is running via webhook!"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=10000)