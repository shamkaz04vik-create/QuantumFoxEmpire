import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from config import BOT_TOKEN, ADMIN_ID, VPN_PARTNERS
from ai import ai_answer
from db import (
    init_db, add_user, log_message,
    set_premium, add_balance
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =====================================================
# /start + реферал
# =====================================================

@dp.message(CommandStart())
async def start_cmd(message: Message):

    args = message.text.split()

    ref = None
    if len(args) > 1 and args[1].isdigit():
        ref = int(args[1])

    username = message.from_user.username or "unknown"

    await add_user(message.from_user.id, username, ref)

    text = (
        "🔥 Добро пожаловать в QuantumFox Empire!\n\n"
        "Пиши любое сообщение — я отвечу.\n"
        "Меню: /menu"
    )

    await message.answer(text)


# =====================================================
# Меню
# =====================================================

@dp.message(Command("menu"))
async def menu(message: Message):
    await message.answer(
        "⚙️ *Меню*\n\n"
        "/vpn — VPN сервисы\n"
        "/premium — Premium\n"
        "/pay — Оплата\n"
        "/admin — Админ панель",
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
        f"🔐 *VPN сервисы*\n\n"
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
        "💎 Premium доступ — 5 USDT\n"
        "Оплатить: /pay",
        parse_mode="Markdown"
    )


# =====================================================
# Оплата
# =====================================================

@dp.message(Command("pay"))
async def pay(message: Message):
    try:
        admin = await bot.get_chat(ADMIN_ID)
        admin_username = admin.username or "admin"
    except:
        admin_username = "admin"

    await message.answer(
        "💰 *Оплата Premium*\n\n"
        "Отправьте 5 USDT (TRC20) на адрес:\n"
        "`TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`\n\n"
        f"После оплаты напишите админу: @{admin_username}",
        parse_mode="Markdown"
    )


# =====================================================
# Админ панель
# =====================================================

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Нет доступа.")

    await message.answer(
        "🛠 *Админ панель*\n\n"
        "/setpremium ID\n"
        "/addbalance ID AMOUNT\n"
        "/broadcast TEXT",
        parse_mode="Markdown"
    )


# Выдать премиум
@dp.message(Command("setpremium"))
async def cmd_setpremium(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await message.answer("Формат:\n/setpremium USER_ID")

    await set_premium(int(parts[1]), True)
    await message.answer("Premium выдан!")


# Добавить баланс
@dp.message(Command("addbalance"))
async def cmd_addbalance(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) != 3:
        return await message.answer("Формат:\n/addbalance USER_ID AMOUNT")

    user_id, amount = parts[1], parts[2]

    if not user_id.isdigit():
        return await message.answer("USER_ID должен быть числом")

    try:
        amount = float(amount)
    except:
        return await message.answer("AMOUNT должно быть числом")

    await add_balance(int(user_id), amount)
    await message.answer("Баланс пополнен!")


# Рассылка
@dp.message(Command("broadcast"))
async def broadcast(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/broadcast", "").strip()

    if not text:
        return await message.answer("Текст пустой.")

    await message.answer("Рассылка запущена (реализация позже).")


# =====================================================
# ИИ чат (ПОСЛЕДНИЙ ХЕНДЛЕР!)
# =====================================================

@dp.message(F.text & ~F.text.startswith("/"))
async def ai_chat(message: Message):
    user_id = message.from_user.id
    text = message.text

    answer = await ai_answer(text)

    await log_message(user_id, text, answer)
    await message.answer(answer)


# =====================================================
# MAIN
# =====================================================

async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())