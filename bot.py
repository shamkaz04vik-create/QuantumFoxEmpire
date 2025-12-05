from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN, ADMIN_ID, VPN_PARTNERS
from ai import ai_answer
from db import add_user, log_message, set_premium, add_balance

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =====================================================
# /start — регистрация + приветствие
# =====================================================
@dp.message(CommandStart())
async def start_cmd(message: Message):
    await add_user(message.from_user.id, message.from_user.username)
    text = (
        "🔥 Добро пожаловать в QuantumFox Empire!\n\n"
        "Я — умный ИИ-бот, помощник и инструмент заработка.\n"
        "Просто напиши любое сообщение — я отвечу.\n\n"
        "📌 Команды:\n"
        "/menu — открыть меню\n"
    )
    await message.answer(text)

# =====================================================
# Меню
# =====================================================
@dp.message(F.text == "/menu")
async def menu(message: Message):
    await message.answer(
        "⚙️ *Меню бота*\n\n"
        "1️⃣ ИИ чат — просто напиши сообщение\n"
        "2️⃣ VPN сервисы — /vpn\n"
        "3️⃣ Premium — /premium\n"
        "4️⃣ Баланс и оплата — /pay\n"
        "5️⃣ Админ панель — /admin (если доступно)",
        parse_mode="Markdown"
    )

# =====================================================
# VPN
# =====================================================
@dp.message(F.text == "/vpn")
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

# =====================================================
# Premium
# =====================================================
@dp.message(F.text == "/premium")
async def premium(message: Message):
    await message.answer(
        "💎 *Premium доступ*\n\n"
        "Преимущества:\n"
        "- Безлимитные запросы к ИИ\n"
        "- Ускоренная скорость\n"
        "- Приоритетная поддержка\n\n"
        "Стоимость: 5 USDT\n"
        "Оплата — команда /pay",
        parse_mode="Markdown"
    )

# =====================================================
# Оплата
# =====================================================
@dp.message(F.text == "/pay")
async def pay(message: Message):
    await message.answer(
        "💰 *Пополнение баланса*\n\n"
        "Сейчас доступен только ручной способ.\n\n"
        "Отправь 5 USDT (TRC20) на адрес:\n"
        "`TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`\n\n"
        "После оплаты напиши админу:\n"
        f"@admin\n\n"
        "После подтверждения Premium активируется.",
        parse_mode="Markdown"
    )

# =====================================================
# Админ панель
# =====================================================
@dp.message(F.text == "/admin")
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ У тебя нет доступа.")
    await message.answer(
        "🛠 *Админ панель*\n\n"
        "/setpremium USER_ID — выдать премиум\n"
        "/addbalance USER_ID SUM — пополнить баланс\n"
        "/broadcast TEXT — рассылка",
        parse_mode="Markdown"
    )

# --- Выдача премиума
@dp.message(F.text.startswith("/setpremium"))
async def admin_setpremium(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("Формат:\n/setpremium USER_ID")

    uid = int(parts[1])
    await set_premium(uid, True)
    await message.answer("Премиум выдан!")

# --- Пополнение баланса
@dp.message(F.text.startswith("/addbalance"))
async def admin_addbalance(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) < 3:
        return await message.answer("Формат:\n/addbalance USER_ID SUM")

    uid = int(parts[1])
    amt = float(parts[2])
    await add_balance(uid, amt)
    await message.answer("Баланс пополнен!")

# =====================================================
# ИИ Чат
# =====================================================
@dp.message(F.text)
async def ai_chat(message: Message):
    user_text = message.text

    ai_reply = await ai_answer(user_text)

    await log_message(message.from_user.id, user_text, ai_reply)

    await message.answer(ai_reply)