# handlers.py
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from db import add_user_if_not_exists, get_user, list_partners, record_partner_click
from ai import ai_answer
from payments import create_crypto_invoice, manual_payment_instructions
from config import VPN_PARTNERS
import time

router = Router()

def main_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("🎛 Профиль"), KeyboardButton("💰 Заработок")],
        [KeyboardButton("🧰 Инструменты"), KeyboardButton("💼 Услуги")],
        [KeyboardButton("🧑‍🤝‍🧑 Реферальная система"), KeyboardButton("🔒 VPN Партнёрки")],
        [KeyboardButton("🤖 ИИ"), KeyboardButton("📤 Сообщить оплату")]
    ], resize_keyboard=True)
    return kb

@router.message(Command("start"))
async def cmd_start(m: Message):
    # parse ref param if present: /start 12345
    args = m.get_args() or ""
    ref = None
    if args.isdigit():
        ref = int(args)
    await add_user_if_not_exists(m.from_user.id, m.from_user.username, m.from_user.first_name, ref)
    await m.answer(f"Привет, {m.from_user.first_name}! Добро пожаловать в QuantumFoxEmpire.", reply_markup=main_kb())

@router.message(lambda m: m.text == "🎛 Профиль")
async def profile(m: Message):
    row = await get_user(m.from_user.id)
    if not row:
        await m.answer("Вы не зарегистрированы. Отправь /start")
        return
    balance = row[4] if row[4] is not None else 0
    vip_until = row[6] if row[6] is not None else 0
    vip = "Нет"
    if vip_until and vip_until > int(time.time()):
        vip = f"VIP до {time.strftime('%Y-%m-%d', time.localtime(vip_until))}"
    await m.answer(f"ID: {m.from_user.id}\nИмя: {m.from_user.first_name}\nБаланс: {balance} ₽\n{vip}")

@router.message(lambda m: m.text == "🧑‍🤝‍🧑 Реферальная система")
async def referral(m: Message):
    me = (await m.bot.get_me()).username
    link = f"https://t.me/{me}?start={m.from_user.id}"
    await m.answer(f"Ваша реферальная ссылка:\n{link}")

@router.message(lambda m: m.text == "🔒 VPN Партнёрки")
async def vpn_menu(m: Message):
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("⚡ Молния VPN")],
        [KeyboardButton("🛡 Kovalenko VPN")],
        [KeyboardButton("🔙 Меню")]
    ], resize_keyboard=True)
    await m.answer("Выберите VPN:", reply_markup=kb)

@router.message(lambda m: m.text in ["⚡ Молния VPN", "🛡 Kovalenko VPN"])
async def vpn_open(m: Message):
    uid = m.from_user.id
    if m.text.startswith("⚡"):
        url = VPN_PARTNERS["molniya"].format(user=uid)
        name = "Молния VPN"
        pid = 1
    else:
        url = VPN_PARTNERS["kovalenko"].format(user=uid)
        name = "Kovalenko VPN"
        pid = 2
    # record click
    await record_partner_click(pid, uid)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Перейти к {name}", url=url)]
    ])
    await m.answer(f"{name} — твоя реферальная ссылка:", reply_markup=kb)

# AI: simple use: user types "ai: <text>"
@router.message()
async def default_handler(m: Message):
    text = (m.text or "").strip()
    if not text:
        return
    if text.lower().startswith("ai:"):
        prompt = text[3:].strip()
        await m.answer("Запрос к ИИ... ⏳")
        out = await ai_answer(prompt)
        await m.answer(out)
        return

    if text == "💰 Заработок":
        await m.answer("Варианты:\n1) Реферальная система\n2) VPN партнерки\n3) Продажа услуг", reply_markup=main_kb())
        return

    if text == "📤 Сообщить оплату":
        instr = await manual_payment_instructions()
        await m.answer(f"Инструкции по оплате:\n{instr['instructions']}\nПосле оплаты отправь скриншот в чат и нажми '🔙 Меню' для возврата.")
        return

    # fallback
    await m.answer("Не понял. Напиши ai: <текст> для ИИ либо выбери пункт меню.", reply_markup=main_kb())