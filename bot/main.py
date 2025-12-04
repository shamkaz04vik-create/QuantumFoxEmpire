from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from config import BOT_TOKEN
from ai import ai_answer
from db import add_user, log_message, init_db, close_db
from aiogram import Router

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# ----------------------------------------------------
# START
# ----------------------------------------------------
@router.message(CommandStart())
async def start_cmd(message: Message):
    await add_user(message.from_user.id, message.from_user.username)
    await message.answer("Привет! Я умный чат-бот. Напиши сообщение 👇")


# ----------------------------------------------------
# ЧАТ
# ----------------------------------------------------
@router.message(F.text)
async def ai_chat(message: Message):
    user_text = message.text
    ai_text = await ai_answer(user_text)

    await log_message(message.from_user.id, user_text, ai_text)
    await message.answer(ai_text)


# ----------------------------------------------------
# STARTUP & SHUTDOWN
# ----------------------------------------------------
@dp.startup()
async def on_startup(dispatcher):
    print("Бот запускается...")
    await init_db()
    print("База инициализирована.")

@dp.shutdown()
async def on_shutdown(dispatcher):
    await close_db()
    print("База закрыта.")


# ----------------------------------------------------
# RUN
# ----------------------------------------------------
def main():
    dp.run_polling(bot)


if __name__ == "__main__":
    main()