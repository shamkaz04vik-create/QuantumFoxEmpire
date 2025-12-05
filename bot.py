# bot.py
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiohttp import web

from config import BOT_TOKEN, ADMIN_ID, VPN_PARTNERS
from ai import ai_answer
from db import add_user, log_message

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# /start
@dp.message(Command("start"))
async def start(message: Message):
    await add_user(message.from_user.id, message.from_user.username or "")
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
async def menu(message: Message):
    await message.answer(
        "⚙️ *Меню бота*\n\n"
        "1️⃣ ИИ чат — просто напиши сообщение\n"
        "2️⃣ VPN — /vpn\n"
        "3️⃣ Premium — /premium\n"
        "4️⃣ Оплата — /pay\n",
        parse_mode="Markdown"
    )

@dp.message(Command("vpn"))
async def vpn_menu(message: Message):
    user = message.from_user.id
    molniya = VPN_PARTNERS.get("molniya", "").format(user=user)
    kovalenko = VPN_PARTNERS.get("kovalenko", "").format(user=user)
    await message.answer(f"⚡ Molniya: {molniya}\n🛡 Kovalenko: {kovalenko}")

@dp.message(F.text)
async def ai_chat(message: Message):
    text = message.text or ""
    ai_reply = await ai_answer(text)
    # log_message может бросить, если db не готов — тогда в лог упадёт понятная ошибка
    await log_message(message.from_user.id, text, ai_reply)
    await message.answer(ai_reply)


# Webhook handler for Render
async def handle(request: web.Request):
    data = await request.json()
    await dp.feed_webhook_update(bot, data)
    return web.Response(text="ok")