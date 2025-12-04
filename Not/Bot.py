import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode

from db import db
from ai import ai_answer

# 🔥 Твой токен
TOKEN = "8456865406:AAGqqDLt4PpMf5QrDEPr7dDXymtTb_eN1_o"

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)


# ------------------ КЛАВИАТУРЫ ------------------

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎛 Профиль")],
            [KeyboardButton(text="💰 Заработок")],
            [KeyboardButton(text="🤖 ИИ Помощник")],
            [KeyboardButton(text="🧰 Инструменты")],
            [KeyboardButton(text="💼 Услуги")],
            [KeyboardButton(text="🧑‍🤝‍🧑 Реферальная система")],
            [KeyboardButton(text="🔒 VPN Партнёрки")],
        ],
        resize_keyboard=True
    )


def back_menu():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True
    )


# ------------------ START ------------------

@dp.message(Command("start"))
async def start(message: types.Message):
    await db.add_user(message.from_user.id)

    username = (await bot.get_me()).username

    ref_id = message.text.split(" ")[1] if len(message.text.split()) > 1 else None
    if ref_id and ref_id.isdigit() and int(ref_id) != message.from_user.id:
        await db.add_referral(int(ref_id), message.from_user.id)

    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n"
        f"Добро пожаловать в QuantumFoxEmpire.\n\n"
        f"Выберите действие:",
        reply_markup=main_menu()
    )


# ------------------ НАЗАД ------------------

@dp.message(lambda m: m.text == "🔙 Назад")
async def back(message: types.Message):
    await message.answer("🔝 Главное меню:", reply_markup=main_menu())


# ------------------ ПРОФИЛЬ ------------------

@dp.message(lambda m: m.text == "🎛 Профиль")
async def profile(message: types.Message):
    user = await db.get_user(message.from_user.id)
    refs = await db.count_refs(message.from_user.id)

    await message.answer(
        f"📊 <b>Ваш профиль</b>\n\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"👤 Имя: {message.from_user.first_name}\n"
        f"👥 Рефералов: <b>{refs}</b>\n"
        f"⚡ Статус: Активный",
        reply_markup=back_menu()
    )


# ------------------ ИИ ПОМОЩНИК ------------------

@dp.message(lambda m: m.text == "🤖 ИИ Помощник")
async def ai_start(message: types.Message):
    await message.answer(
        "🤖 Отправь свой запрос, и я подключу ИИ-модель!",
        reply_markup=back_menu()
    )


@dp.message(lambda m: m.text not in [
    "🎛 Профиль", "💰 Заработок", "🤖 ИИ Помощник",
    "🧰 Инструменты", "💼 Услуги", "🧑‍🤝‍🧑 Реферальная система",
    "🔒 VPN Партнёрки", "🔙 Назад"
])
async def ai_process(message: types.Message):
    reply = await ai_answer(message.text)
    await message.answer(reply)


# ------------------ ЗАРАБОТОК ------------------

@dp.message(lambda m: m.text == "💰 Заработок")
async def earning(message: types.Message):
    await message.answer(
        "💰 <b>Способы заработка:</b>\n\n"
        "1️⃣ Реферальная система\n"
        "2️⃣ VPN партнёрки\n"
        "3️⃣ Продвижение услуг\n",
        reply_markup=back_menu()
    )


# ------------------ ИНСТРУМЕНТЫ ------------------

@dp.message(lambda m: m.text == "🧰 Инструменты")
async def tools(message: types.Message):
    await message.answer(
        "🧰 Инструменты (в разработке)",
        reply_markup=back_menu()
    )


# ------------------ УСЛУГИ ------------------

@dp.message(lambda m: m.text == "💼 Услуги")
async def services(message: types.Message):
    await message.answer(
        "<b>💼 Услуги QuantumFoxEmpire:</b>\n"
        "• Создание Telegram-ботов\n"
        "• Дизайн\n"
        "• Сайты\n"
        "• Продвижение\n",
        reply_markup=back_menu()
    )


# ------------------ РЕФЕРАЛЬНАЯ СИСТЕМА ------------------

@dp.message(lambda m: m.text == "🧑‍🤝‍🧑 Реферальная система")
async def referral(message: types.Message):
    username = (await bot.get_me()).username
    link = f"https://t.me/{username}?start={message.from_user.id}"

    refs = await db.count_refs(message.from_user.id)

    await message.answer(
        "<b>🧑‍🤝‍🧑 Реферальная программа</b>\n\n"
        f"🔗 Твоя ссылка:\n{link}\n\n"
        f"👥 Приглашено: <b>{refs}</b>",
        reply_markup=back_menu()
    )


# ------------------ VPN ------------------

@dp.message(lambda m: m.text == "🔒 VPN Партнёрки")
async def vpn(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚡ Молния VPN")],
            [KeyboardButton(text="🛡 Kovalenko VPN")],
            [KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True
    )
    await message.answer("🔒 Выберите VPN:", reply_markup=kb)


@dp.message(lambda m: m.text in ["⚡ Молния VPN", "🛡 Kovalenko VPN"])
async def vpn_links(message: types.Message):
    user = message.from_user.id
    links = {
        "⚡ Молния VPN": f"https://t.me/molniya_vpn_bot?start=john0_8_{user}",
        "🛡 Kovalenko VPN": f"https://t.me/Kovalenkovpn_bot?start=john0_8_{user}"
    }
    await message.answer(f"🔥 Ваша ссылка:\n{links[message.text]}")


# ------------------ START POLLING ------------------

async def main():
    await db.connect()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())