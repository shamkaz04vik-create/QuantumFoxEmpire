# bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import router as user_router
from admin import router as admin_router
from db import init_db, ensure_default_partners

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_bot():
    # init DB
    await init_db()
    await ensure_default_partners()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(user_router)
    dp.include_router(admin_router)

    logger.info("Starting polling (useful for local testing)...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())