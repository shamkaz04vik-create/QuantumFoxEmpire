import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8456865406  # твой Telegram ID (можно менять)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ----------- Главное меню -----------
def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="💼 Услуги")
    kb.button(text="💰 Заработок")
    kb.button(text="👤 Профиль")
    kb.button(text="📞 Поддержка")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

# ----------- Админ меню -----------
def admin_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="📢 Рассылка")
    kb.button(text="📊 Статистика")
    kb.button(text="🔙 Назад")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

# ----------- Команда /start -----------
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "🦊 Quantum Fox Empire\nДобро пожаловать, Админ!",
            reply_markup=main_menu()
        )
    else:
        await message.answer(
            "🦊 Добро пожаловать в Quantum Fox Empire!\nВыберите действие ниже:",
            reply_markup=main_menu()
        )

# ----------- Обработка кнопок -----------
@dp.message()
async def menu_handler(message: types.Message):
    text = message.text

    # Кнопка услуги
    if text == "💼 Услуги":
        await message.answer("💼 Здесь скоро появится каталог услуг!")
    
    # Кнопка заработок
    elif text == "💰 Заработок":
        await message.answer("💰 Скоро здесь появится система заработка!")

    # Кнопка профиль
    elif text == "👤 Профиль":
        await message.answer(f"👤 Ваш ID: {message.from_user.id}")

    # Кнопка поддержка
    elif text == "📞 Поддержка":
        await message.answer("Напишите нам: @your_support")

    # Админские функции
    elif text == "📢 Рассылка" and message.from_user.id == ADMIN_ID:
        await message.answer("Введите текст рассылки:")

    elif text == "📊 Статистика" and message.from_user.id == ADMIN_ID:
        await message.answer("📊 Статистика будет позже.")

    elif text == "🛠 Админ" and message.from_user.id == ADMIN_ID:
        await message.answer("Админ меню:", reply_markup=admin_menu())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())