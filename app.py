from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
import asyncio
from config import BOT_TOKEN
from bot import dp

bot = Bot(token=BOT_TOKEN)
app = FastAPI()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return {"status": "ok"}

@app.get("/")
def home():
    return "Bot running"