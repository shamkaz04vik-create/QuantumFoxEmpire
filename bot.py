from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command

from config import BOT_TOKEN, ADMIN_ID, VPN_PARTNERS
from ai import ai_answer
from db import add_user, log_message

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ===============================
# /start
# ===============================
@dp.message(Command("start"))
async def start(message: Message):
    await add_user(message.from_user.id, message.from_user.username)

    await message.answer(
        "🔥 Добро пожаловать!\n\n"
        "Я — ИИ-бот. Просто напиши сообщение — и я отвечу.\n\n"
        "📌 Команды:\n"
        "/menu — меню\n"
        "/vpn — VPN сервисы\n"
        "/premium — премиум\n"
        "/pay — оплата\n"
    )


# ===============================
# Меню
# ===============================
@dp.message(Command("menu"))
async def menu(message: Message):
    await message.answer(
        "⚙️ *Меню бота*\n\n"
        "1️⃣ ИИ чат — просто напиши сообщение\n"
        "2️⃣ VPN — /vpn\n"
        "3️⃣ Premium — /premium\n"
        "4️⃣ Оплата — /pay\n"
        "5️⃣ Админ панель — /admin",
        parse_mode="Markdown"
    )


# ===============================
# VPN
# ===============================
@dp.message(Command("vpn"))
async def vpn_menu(message: Message):
    user = message.from_user.id
    molniya = VPN_PARTNERS["molniya"].format(user=user)
    kovalenko = VPN_PARTNERS["kovalenko"].format(user=user)

    await message.answer(
        "🔐 *VPN сервисы:* \n\n"
        f"⚡ Molniya VPN:\n{molniya}\n\n"
        f"🛡 Kovalenko VPN:\n{kovalenko}",
        parse_mode="Markdown"
    )


# ===============================
# Premium
# ===============================
@dp.message(Command("premium"))
async def premium(message: Message):
    await message.answer(
        "💎 *Premium*\n\n"
        "Преимущества:\n"
        "- Безлимитный ИИ\n"
        "- Быстрые ответы\n"
        "- Приоритетная очередь\n\n"
        "Цена: 5 USDT\n"
        "Оплата → /pay",
        parse_mode="Markdown"
    )


# ===============================
# Оплата
# ===============================
@dp.message(Command("pay"))
async def pay(message: Message):
    await message.answer(
        "💰 *Оплата*\n\n"
        "Отправь *5 USDT (TRC20)* на адрес:\n"
        "`TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`\n\n"
        "После оплаты — напиши админу: @admin",
        parse_mode="Markdown"
    )


# ===============================
# Админ панель
# ===============================
@dp.message(Command("admin"))
async def admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Нет доступа")

    await message.answer(
        "🛠 *Админ панель*\n\n"
        "Пока доступно только:\n"
        "/broadcast <текст>",
        parse_mode="Markdown"
    )


# ===============================
# ИИ чат
# ===============================
@dp.message(F.text)
async def ai_chat(message: Message):
    text = message.text

    # Ответ ИИ
    ai_reply = await ai_answer(text)

    # Лог в БД
    await log_message(message.from_user.id, text, ai_reply)

    # Ответ пользователю
    await message.answer(ai_reply)