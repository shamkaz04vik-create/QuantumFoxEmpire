from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiohttp import web

from config import BOT_TOKEN, ADMIN_ID, VPN_PARTNERS
from ai import ai_answer
from db import add_user, log_message  # <-- оставляем ТОЛЬКО эти


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =====================================================
# /start
# =====================================================
@dp.message(Command("start"))
async def start(message: Message):
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

# =====================================================
# Меню
# =====================================================
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

# =====================================================
# VPN
# =====================================================
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

# =====================================================
# Premium
# =====================================================
@dp.message(Command("premium"))
async def premium(message: Message):
    await message.answer(
        "💎 *Premium*\n\n"
        "Преимущества:\n"
        "- Безлимитный ИИ\n"
        "- Быстрые ответы\n"
        "- Приоритет\n\n"
        "Цена: 5 USDT\n"
        "Оплата — /pay",
        parse_mode="Markdown"
    )

# =====================================================
# Оплата
# =====================================================
@dp.message(Command("pay"))
async def pay(message: Message):
    await message.answer(
        "💰 *Пополнение*\n\n"
        "Отправь 5 USDT (TRC20) на адрес:\n"
        "`TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`\n\n"
        "После оплаты — напиши админу: @admin",
        parse_mode="Markdown"
    )

# =====================================================
# Админ панель (без функций, которых нет в db)
# =====================================================
@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Нет доступа")

    await message.answer(
        "🛠 *Админ панель*\n\n"
        "‼️ ВНИМАНИЕ: функции setpremium и addbalance отключены.\n"
        "Так как их нет в db.py — временно недоступны.\n\n"
        "Доступно:\n/broadcast TEXT",
        parse_mode="Markdown"
    )

# =====================================================
# ИИ чат
# =====================================================
@dp.message(F.text)
async def ai_chat(message: Message):
    text = message.text

    ai_reply = await ai_answer(text)
    await log_message(message.from_user.id, text, ai_reply)

    await message.answer(ai_reply)

# =====================================================
# Webhook для Render
# =====================================================
async def handle(request: web.Request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()

def setup_webhook(app: web.Application):
    app.router.add_post("/", handle)

def run():
    app = web.Application()
    setup_webhook(app)
    return app

app = run()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)