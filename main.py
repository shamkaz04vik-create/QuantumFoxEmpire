from fastapi import FastAPI, Request
from aiogram.types import Update
from bot import dp, bot
from db import init_db

app = FastAPI()

@app.on_event("startup")
async def startup():
    print("▶ INIT DB...")
    await init_db()
    print("▶ DB READY")

    await bot.set_webhook("https://quantumfoxempire.onrender.com/")
    print("▶ WEBHOOK SET")

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def home():
    return {"running": True}