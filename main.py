import os
import logging
from fastapi import FastAPI, Request, Header, HTTPException
from aiogram.types import Update
from bot import dp, bot
from db import init_db, close_db
from config import WEBHOOK_URL, WEBHOOK_SECRET_TOKEN  # Добавим секретный токен

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
async def startup():
    logger.info("▶ INIT DB")
    try:
        await init_db()
        logger.info("▶ DB OK")
    except Exception as e:
        logger.exception("❌ DB INIT FAILED")
        raise e

    try:
        await bot.set_webhook(WEBHOOK_URL, secret_token=WEBHOOK_SECRET_TOKEN)
        logger.info(f"▶ WEBHOOK OK: {WEBHOOK_URL}")
    except Exception as e:
        logger.exception("❌ WEBHOOK SET FAILED")
        raise e

@app.on_event("shutdown")
async def shutdown():
    logger.info("▶ SHUTDOWN")
    try:
        await bot.delete_webhook()
        logger.info("▶ WEBHOOK DELETED")
    except Exception as e:
        logger.warning(f"❌ FAILED TO DELETE WEBHOOK: {e}")

    try:
        await close_db()
        logger.info("▶ DB CLOSED")
    except Exception as e:
        logger.warning(f"❌ FAILED TO CLOSE DB: {e}")

@app.post("/webhook")
async def webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(None)
):
    # Проверка секретного токена
    if x_telegram_bot_api_secret_token != WEBHOOK_SECRET_TOKEN:
        logger.warning("❌ Invalid Telegram secret token")
        raise HTTPException(status_code=403, detail="Invalid secret token")

    try:
        data = await request.json()
        update = Update(**data)
        await dp.feed_update(bot, update)
    except Exception as e:
        logger.exception("❌ Failed to process update")
        # Возвращаем 200, чтобы Telegram не повторял webhook слишком часто
        return {"ok": False, "error": str(e)}

    return {"ok": True}

@app.get("/")
async def home():
    return {"running": True}