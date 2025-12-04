# app.py
import os
import asyncio
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
import uvicorn

from config import BOT_TOKEN, WEBHOOK_URL
from db import init_db, ensure_default_partners
from handlers import router as user_router
from admin import router as admin_router

app = FastAPI()

# create bot & dispatcher to be used by webhook
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(user_router)
dp.include_router(admin_router)

@app.on_event("startup")
async def startup():
    await init_db()
    await ensure_default_partners()
    # set webhook
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)

@app.post("/webhook")
async def process_webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def home():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))