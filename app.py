# app.py
import os
import asyncio
from fastapi import FastAPI, Request
from aiogram import types
from aiogram.types import Update
import uvicorn

from bot import dp, bot, start_bg

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://quantumfoxempire.onrender.com/webhook")
PORT = int(os.getenv("PORT", "10000"))

app = FastAPI()

@app.on_event("startup")
async def startup():
    # init DB and partners
    await start_bg()
    # set webhook
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    print("Webhook set to", WEBHOOK_URL)

@app.post("/webhook")
async def process_webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    # feed update to dispatcher
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def home():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=PORT)