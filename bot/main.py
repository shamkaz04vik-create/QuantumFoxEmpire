import asyncio
from bot.main import dp, bot
from db import init_db

async def main():
    print("Инициализация базы...")
    await init_db()

    print("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
