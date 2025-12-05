# bot.py — определения Bot, Dispatcher и хендлеров
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiohttp import web

from config import BOT_TOKEN, ADMIN_ID, VPN_PARTNERS
from ai import ai_answer
from db import add_user, log_message  # используем только эти две (без лишних зависимостей)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: Message):
    # добавим пользователя
    await add_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "🔥 Добро пожаловать!\n\n"
        "Я — ИИ-бот. Просто напиши сообщение и я отвечу.\n\n"
        "📌 Команды:\n"
        "/menu — меню\n"
        "/vpn — VPN сервисы\n"
        "/premium — премиум\n"
        "/pay — оплата\n"
    )

@dp.message(Command("menu"))
async def menu_handler(message: Message):
    await message.answer(
        "⚙️ *Меню бота*\n\n"
        "1️⃣ ИИ чат — просто напиши сообщение\n"
        "2️⃣ VPN — /vpn\n"
        "3️⃣ Premium — /premium\n"
        "4️⃣ Оплата — /pay\n"
        "5️⃣ Админ панель — /admin",
        parse_mode="Markdown"
    )

@dp.message(Command("vpn"))
async def vpn_handler(message: Message):
    user = message.from_user.id
    molniya = VPN_PARTNERS["molniya"].format(user=user)
    kovalenko = VPN_PARTNERS["kovalenko"].format(user=user)
    await message.answer(
        "🔐 *VPN сервисы:* \n\n"
        f"⚡ Molniya VPN:\n{molniya}\n\n"
        f"🛡 Kovalenko VPN:\n{kovalenko}",
        parse_mode="Markdown"
    )

@dp.message(Command("premium"))
async def premium_handler(message: Message):
    await message.answer(
        "💎 *Premium*\n\n"
        "Преимущества:\n- Безлимитный ИИ\n- Быстрые ответы\n- Приоритет\n\n"
        "Цена: 5 USDT\nОплата — /pay",
        parse_mode="Markdown"
    )

@dp.message(Command("pay"))
async def pay_handler(message: Message):
    await message.answer(
        "💰 *Пополнение*\n\n"
        "Отправь 5 USDT (TRC20) на адрес:\n"
        "`TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`\n\n"
        "После оплаты — напиши админу.",
        parse_mode="Markdown"
    )

@dp.message(Command("admin"))
async def admin_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Нет доступа")
    await message.answer(
        "🛠 *Админ панель*\n\n"
        "‼️ ВНИМАНИЕ: некоторые функции (setpremium/addbalance) могут быть отключены\n"
        "Доступно:\n/broadcast TEXT",
        parse_mode="Markdown"
    )

@dp.message(F.text)
async def ai_chat(message: Message):
    text = message.text
    ai_reply = await ai_answer(text)
    await log_message(message.from_user.id, text, ai_reply)
    await message.answer(ai_reply)

# --- Webhook helper (если нужен внутри файла — но main.py будет ставить webhook)
async def handle_webhook(request: web.Request):
    update = await request.json()
    await dp.feed_update(bot, update)
    return web.Response(text="ok")