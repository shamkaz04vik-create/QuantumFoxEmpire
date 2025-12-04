import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7209803923  # твой Telegram ID

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

# ----------- Меню услуг -----------
def services_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="🧑‍💻 Создание ботов")
    kb.button(text="🎨 Дизайн")
    kb.button(text="📢 Реклама и продвижение")
    kb.button(text="📱 Создание сайтов")
    kb.button(text="🔙 Назад")
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

    # --- Каталог услуг ---
    if text == "💼 Услуги":
        await message.answer("Выберите услугу:", reply_markup=services_menu())

    elif text == "🧑‍💻 Создание ботов":
        await message.answer(
            "🧑‍💻 *Создание Telegram-ботов*\n"
            "Цена: от 5000 ₽\n\n"
            "Опишите задачу, и мы обсудим детали!",
            parse_mode="Markdown"
        )

    elif text == "🎨 Дизайн":
        await message.answer(
            "🎨 *Дизайн (логотипы, баннеры, обложки)*\n"
            "Цена: от 1000 ₽",
            parse_mode="Markdown"
        )

    elif text == "📢 Реклама и продвижение":
        await message.answer(
            "📢 *Продвижение Telegram-каналов*\n"
            "Цена: индивидуально.",
            parse_mode="Markdown"
        )

    elif text == "📱 Создание сайтов":
        await message.answer(
            "📱 *Создание сайтов под ключ*\n"
            "Цена: от 10 000 ₽",
            parse_mode="Markdown"
        )

    elif text == "🔙 Назад":
        await message.answer("Главное меню:", reply_markup=main_menu())

    # --- Заработок ---
    elif text == "💰 Заработок":
        await message.answer("💰 Здесь скоро появится система заработка!")

    # --- Профиль ---
    elif text == "👤 Профиль":
        await message.answer(f"👤 Ваш Telegram ID: {message.from_user.id}")

    # --- Поддержка ---
    elif text == "📞 Поддержка":
        await message.answer("Напишите нам: @your_support")

    # --- Админские кнопки ---
    elif text == "🛠 Админ" and message.from_user.id == ADMIN_ID:
        await message.answer("Админ меню:", reply_markup=admin_menu())

    elif text == "📢 Рассылка" and message.from_user.id == ADMIN_ID:
        await message.answer("Введите текст рассылки (функция скоро будет добавлена).")

    elif text == "📊 Статистика" and message.from_user.id == ADMIN_ID:
        await message.answer("📊 Статистика появится позже.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())