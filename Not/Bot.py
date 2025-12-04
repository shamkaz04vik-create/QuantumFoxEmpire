import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, WEBHOOK_URL
from handlers import router as user_router
from admin import router as admin_router
from database import db_connect, init_db

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def main():
    db = await db_connect()
    await init_db(db)

    dp.include_router(user_router)
    dp.include_router(admin_router)

    await bot.set_webhook(WEBHOOK_URL)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())