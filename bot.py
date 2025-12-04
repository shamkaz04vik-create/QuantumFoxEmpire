import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from config import BOT_TOKEN, ADMIN_ID, VPN_PARTNERS
from ai import ai_answer
from db import (
    init_db, add_user, log_message,
    set_premium, add_balance, log_payment
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =====================================================
# /start + рефералки
# =====================================================

@dp.message(CommandStart())
async def start_cmd(message: Message):
    args = message.text.split()

    ref_id = None
    if len(args) > 1 and args[1].isdigit():
        ref_id = int(args[1])

    await add_user(message.from_user.id, message.from_user.username, ref_id)

    text = (
        "🔥 Добро пожаловать в QuantumFox Empire!\n\n"
        "Я — умный ИИ-бот, помощник и инструмент заработка.\n"
        "Пиши любое сообщение — я отвечу!\n\n"
        "📌 Дополнительно:\n"
        "/menu — открыть меню\n"
    )

    await message.answer(text)


# =====================================================
# Главное меню
# =====================================================

@dp.message(F.text == "/menu")
async def menu(message: Message):
    await message.answer(
        "⚙️ *Меню бота*\n\n"
        "1️⃣ ИИ чат — просто напиши сообщение\n"
        "2️⃣ VPN сервисы — /vpn\n"
        "3️⃣ Premium — /premium\n"
        "4️⃣ Баланс и оплата — /pay\n"
        "5️⃣ Админ панель — /admin (для тебя)",
        parse_mode="Markdown"
    )


# =====================================================
# VPN партнёрки
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
        "- Повышенная скорость ответов\n"
        "- Приоритетная поддержка\n\n"
        "Стоимость: 5 USDT\n"
        "Оплатить: /pay",
        parse_mode="Markdown"
    )


# =====================================================
# Оплата
# =====================================================

@dp.message(F.text == "/pay")
async def pay(message: Message):
    await message.answer(
        "💰 *Пополнение баланса*\n\n"
        "Пока доступен ручной метод оплаты.\n\n"
        "Отправьте 5 USDT (TRC20) на адрес:\n"
        "`TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`\n\n"
        "После перевода напишите админу:\n"
        f"@{(await bot.get_chat(ADMIN_ID)).username}\n\n"
        "Админ подтвердит оплату 👉 Premium активируется.",
        parse_mode="Markdown"
    )


# =====================================================
# Админ панель
# =====================================================

@dp.message(F.text == "/admin")
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Нет доступа.")

    await message.answer(
        "🛠 *Админ панель*\n\n"
        "/setpremium USER_ID — выдать премиум\n"
        "/addbalance USER_ID AMOUNT — пополнить баланс\n"
        "/broadcast ТЕКСТ — рассылка",
        parse_mode="Markdown"
    )


# Админ: выдача премиума
@dp.message(F.text.startswith("/setpremium"))
async def cmd_setpremium(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("Формат: /setpremium USER_ID")

    user_id = int(parts[1])
    await set_premium(user_id, True)
    await message.answer("Готово! Premium выдан.")


# Админ: баланс
@dp.message(F.text.startswith("/addbalance"))
async def cmd_addbalance(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) < 3:
        return await message.answer("Формат: /addbalance USER_ID AMOUNT")

    user_id = int(parts[1])
    amount = float(parts[2])

    await add_balance(user_id, amount)
    await message.answer("Баланс пополнен!")


# Админ рассылка
@dp.message(F.text.startswith("/broadcast"))
async def broadcast(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/broadcast", "").strip()

    if not text:
        return await message.answer("Текст пустой.")

    await message.answer("Рассылка началась… (функцию можно доработать)")


# =====================================================
# ИИ чат
# =====================================================

@dp.message(F.text)
async def ai_chat(message: Message):
    user_id = message.from_user.id
    user_text = message.text

    ai_response = await ai_answer(user_text)

    await message.answer(ai_response)

    # Логируем для истории
    await log_message(user_id, user_text, ai_response)


# =====================================================
# MAIN
# =====================================================

async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())