import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ------------------ TOKEN ------------------
TOKEN = "8456865406:AAGqqDLt4PpMf5QrDEPr7dDXymtTb_eN1_o"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ------------------ КЛАВИАТУРЫ ------------------

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎛 Профиль")],
            [KeyboardButton(text="💰 Заработок")],
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
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n"
        f"Добро пожаловать в QuantumFoxEmpire.\n\n"
        f"Выберите действие:",
        reply_markup=main_menu()
    )


# ------------------ НАЗАД ------------------

@dp.message(lambda msg: msg.text == "🔙 Назад")
async def back(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_menu())


# ------------------ ПРОФИЛЬ ------------------

@dp.message(lambda msg: msg.text == "🎛 Профиль")
async def profile(message: types.Message):
    await message.answer(
        f"📊 *Ваш профиль*\n\n"
        f"🆔 ID: `{message.from_user.id}`\n"
        f"👤 Имя: {message.from_user.first_name}\n"
        f"⚡ Статус: Активный пользователь",
        parse_mode="Markdown",
        reply_markup=back_menu()
    )


# ------------------ ЗАРАБОТОК ------------------

@dp.message(lambda msg: msg.text == "💰 Заработок")
async def earning(message: types.Message):
    await message.answer(
        "💰 *Способы заработка:*\n\n"
        "1️⃣ Реферальная система\n"
        "2️⃣ VPN партнёрки\n"
        "3️⃣ Продвижение услуг\n\n"
        "Выберите способ 👇",
        parse_mode="Markdown",
        reply_markup=back_menu()
    )


# ------------------ ИНСТРУМЕНТЫ ------------------

@dp.message(lambda msg: msg.text == "🧰 Инструменты")
async def tools(message: types.Message):
    await message.answer(
        "🧰 Инструменты:\n"
        "• Генерация текста\n"
        "• Формирование ссылок\n"
        "• Поддержка проекта\n"
        "• Работа с сообщениями\n\n"
        "Сервис в разработке ⚡",
        reply_markup=back_menu()
    )


# ------------------ УСЛУГИ ------------------

@dp.message(lambda msg: msg.text == "💼 Услуги")
async def services(message: types.Message):
    await message.answer(
        "💼 *Услуги QuantumFoxEmpire:*\n\n"
        "• Создание Telegram-ботов\n"
        "• Дизайн\n"
        "• Разработка сайтов\n"
        "• Продвижение\n"
        "• Партнёрская интеграция\n\n"
        "Напишите, что вам нужно 👇",
        parse_mode="Markdown",
        reply_markup=back_menu()
    )


# ------------------ РЕФЕРАЛКИ ------------------

@dp.message(lambda msg: msg.text == "🧑‍🤝‍🧑 Реферальная система")
async def referral(message: types.Message):
    username = (await bot.get_me()).username
    ref_link = f"https://t.me/{username}?start={message.from_user.id}"

    await message.answer(
        "🧑‍🤝‍🧑 *Реферальная программа*\n\n"
        "Приглашайте людей и получайте бонусы!\n\n"
        f"🔗 Ваша ссылка:\n{ref_link}",
        parse_mode="Markdown",
        reply_markup=back_menu()
    )


# ------------------ VPN ПАРТНЕРКИ ------------------

@dp.message(lambda msg: msg.text == "🔒 VPN Партнёрки")
async def vpn_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚡ Молния VPN")],
            [KeyboardButton(text="🛡 Kovalenko VPN")],
            [KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True
    )
    await message.answer("🔒 Выберите VPN:", reply_markup=keyboard)


@dp.message(lambda msg: msg.text in ["⚡ Молния VPN", "🛡 Kovalenko VPN"])
async def vpn_links(message: types.Message):
    user_id = message.from_user.id

    links = {
        "⚡ Молния VPN": f"https://t.me/molniya_vpn_bot?start=john0_8_{user_id}",
        "🛡 Kovalenko VPN": f"https://t.me/Kovalenkovpn_bot?start=john0_8_{user_id}",
    }

    vpn = message.text
    await message.answer(
        f"🔥 *{vpn}*\n\n"
        f"Вот ваша персональная ссылка:\n{links[vpn]}\n\n"
        f"После оплаты вы получите бонусы 💸",
        parse_mode="Markdown"
    )


# ------------------ START BOT ------------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())