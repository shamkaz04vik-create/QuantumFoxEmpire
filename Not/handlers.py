# handlers.py
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from config import VPN_PARTNERS
from ai import ai_answer
from db import add_or_update_user, set_referrer, add_event, get_user
from payments import simulate_purchase
import time

router = Router()

def main_keyboard():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("🎛 Профиль"), KeyboardButton("💰 Заработок")],
        [KeyboardButton("🧰 Инструменты"), KeyboardButton("💼 Услуги")],
        [KeyboardButton("🧑‍🤝‍🧑 Реферальная система"), KeyboardButton("🔒 VPN Партнёрки")],
        [KeyboardButton("🧠 AI"), KeyboardButton("💳 Купить VIP")]
    ], resize_keyboard=True)
    return kb

@router.message(Command("start"))
async def start_cmd(message: Message):
    # если в /start пришёл параметр (ref)
    await add_or_update_user(message.from_user)
    # check for start payload
    payload = None
    if message.text and len(message.text.split()) > 1:
        payload = message.text.split(maxsplit=1)[1]
        # если payload — число (ref id)
        try:
            ref = int(payload)
            await set_referrer(message.from_user.id, ref)
        except:
            pass

    await add_event(message.from_user.id, "start", payload or "")
    await message.answer(f"Привет, {message.from_user.first_name}! Это QuantumFoxEmpire bot.\nВыбери пункт меню 👇", reply_markup=main_keyboard())

# простой профиль
@router.message(lambda m: m.text == "🎛 Профиль")
async def profile(m: Message):
    row = await get_user(m.from_user.id)
    vip_until = row[6] if row else 0
    vip = "Нет"
    if vip_until and vip_until > int(time.time()):
        vip = f"VIP до {time.strftime('%Y-%m-%d', time.localtime(vip_until))}"
    await m.answer(f"ID: `{m.from_user.id}`\nИмя: {m.from_user.first_name}\n{vip}", parse_mode="Markdown")

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
        [KeyboardButton("🔙 Назад")]
    ], resize_keyboard=True)
    await m.answer("Выберите VPN:", reply_markup=kb)

@router.message(lambda m: m.text in ["⚡ Молния VPN", "🛡 Kovalenko VPN"])
async def send_vpn(m: Message):
    uid = m.from_user.id
    if m.text.startswith("⚡"):
        url = VPN_PARTNERS["molniya"].format(uid=uid)
        name = "Молния VPN"
    else:
        url = VPN_PARTNERS["kovalenko"].format(uid=uid)
        name = "Kovalenko VPN"
    await m.answer(f"{name}\nВаша реф. ссылка:\n{url}")

# AI: отправляем запрос к OpenRouter
@router.message(lambda m: m.text == "🧠 AI")
async def ask_ai_menu(m: Message):
    await m.answer("Отправь сообщение, я отвечу через ИИ. Чтобы выйти — отправь /cancel")

# следующий просто перехватывает текст (простая реализация)
@router.message()
async def default_handler(m: Message):
    text = (m.text or "").strip()
    if not text:
        return
    # Если пользователь ранее нажал AI — мы не делаем state machine: простая горячая команда "ai: <text>"
    if text.startswith("ai:"):
        prompt = text[3:].strip()
        await m.answer("Запрос к ИИ... ⏳")
        out = await ai_answer(prompt)
        await m.answer(out)
        return

    # команды покупки VIP
    if text == "💳 Купить VIP":
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton("VIP 30 дней — $7"), KeyboardButton("VIP 1 год — $60")],
            [KeyboardButton("🔙 Назад")]
        ], resize_keyboard=True)
        await m.answer("Выбери план:", reply_markup=kb)
        return

    if text.startswith("VIP 30"):
        res = await simulate_purchase(m.from_user.id, "vip_month")
        await m.answer(res["msg"])
        return
    if text.startswith("VIP 1"):
        res = await simulate_purchase(m.from_user.id, "vip_year")
        await m.answer(res["msg"])
        return

    # простой fallback: показываем меню
    await m.answer("Не понял. Выбери пункт меню:", reply_markup=main_keyboard())