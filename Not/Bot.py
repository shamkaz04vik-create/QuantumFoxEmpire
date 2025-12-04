# bot.py
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from db_utils import (
    init_db, ensure_default_partners, add_user_if_not_exists, get_user_stats,
    list_partners, get_partner, record_partner_click, record_confirmed_purchase,
    create_payout_request, list_payouts, set_payout_status, partner_clicks_stats, total_users_count
)
from datetime import datetime

# config from env
BOT_TOKEN = os.getenv("BOT_TOKEN", "8456865406:AAGqqDLt4PpMf5QrDEPr7dDXymtTb_eN1_o")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7209803923"))
DB_PATH = os.getenv("DB_PATH", "/data/database.db")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# keyboards
def main_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("🎛 Профиль"), KeyboardButton("💰 Заработок")],
        [KeyboardButton("🧰 Инструменты"), KeyboardButton("💼 Услуги")],
        [KeyboardButton("🔒 VPN Партнёрки"), KeyboardButton("🧑‍🤝‍🧑 Реферальная система")],
        [KeyboardButton("📤 Вывести")]
    ], resize_keyboard=True)
    return kb

def back_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton("🔙 Назад")]], resize_keyboard=True)

# simple helper to format partner list
def partner_item_kb(pid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Перейти и поддержать (откроется в новом окне)", callback_data=f"open_partner:{pid}")],
        [InlineKeyboardButton(text="Сообщить оплату (админ)", callback_data=f"report_pay:{pid}")]
    ])

# startup helper to init db and partners
async def prepare():
    await init_db(DB_PATH)
    await ensure_default_partners(DB_PATH)

# /start
@dp.message(CommandStart())
async def on_start(message: types.Message):
    args = message.get_args() or ""
    ref = None
    # support ref<id> or john0_8_<id>
    if args:
        if args.startswith("ref"):
            try:
                ref = int(args[3:])
            except:
                ref = None
        else:
            try:
                parts = args.split("_")
                poss = parts[-1]
                ref = int(poss)
            except:
                ref = None
    created = await add_user_if_not_exists(message.from_user.id, message.from_user.username, message.from_user.first_name, ref, DB_PATH)
    if created:
        if ref:
            await message.answer("Регистрация прошла. Бонусы за реферала начислены.", reply_markup=main_kb())
        else:
            await message.answer("Добро пожаловать! Вы в системе.", reply_markup=main_kb())
    else:
        await message.answer("С возвращением!", reply_markup=main_kb())

# Profile
@dp.message(Command("profile") | (lambda m: m.text == "🎛 Профиль"))
async def profile(message: types.Message):
    uid = message.from_user.id
    stats = await get_user_stats(uid, DB_PATH)
    if not stats:
        await message.answer("Вы не зарегистрированы. Нажмите /start", reply_markup=main_kb())
        return
    await message.answer(
        f"👤 Профиль\n\nID: `{uid}`\nИмя: {message.from_user.full_name}\nБаланс: {stats['balance']:.2f} ₽\nПриглашено: {stats['refs']}",
        parse_mode="Markdown",
        reply_markup=main_kb()
    )

# Referral
@dp.message(lambda m: m.text == "🧑‍🤝‍🧑 Реферальная система")
async def referral(message: types.Message):
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start=john0_8_{message.from_user.id}"
    await message.answer(f"🔁 Реферальная система\nВаша ссылка:\n{link}\n\nПриглашённый получает +10₽, вы — +20₽", reply_markup=main_kb())

# Partners list
@dp.message(lambda m: m.text == "🔒 VPN Партнёрки")
async def partners_list(message: types.Message):
    parts = await list_partners(DB_PATH)
    if not parts:
        await message.answer("Партнёров нет.", reply_markup=main_kb())
        return
    for p in parts:
        pid, name, urlt, cat, pshare, ushare = p
        await message.answer(f"🔹 {name}\nКатегория: {cat}\nКомиссия партнёрки: {pshare*100:.0f}%", reply_markup=partner_item_kb(pid))

# callback open partner
@dp.callback_query(lambda c: c.data and c.data.startswith("open_partner:"))
async def cb_open_partner(query: types.CallbackQuery):
    await query.answer()
    pid = int(query.data.split(":")[1])
    row = await get_partner(DB_PATH, pid)
    if not row:
        await query.message.answer("Партнёр не найден.")
        return
    pid, name, url_template, pshare, ushare = row
    uid = query.from_user.id
    await record_partner_click(pid, uid, DB_PATH)
    url = url_template.format(user=uid)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Перейти к {name}", url=url)]
    ])
    await query.message.answer(f"Вы переходите к {name}. Нажмите кнопку ниже.", reply_markup=kb)

# callback report payment (user reports they paid)
@dp.callback_query(lambda c: c.data and c.data.startswith("report_pay:"))
async def cb_report_pay(query: types.CallbackQuery):
    await query.answer("Запрос отправлен администратору.")
    pid = int(query.data.split(":")[1])
    uid = query.from_user.id
    # send admin a message with quick command to confirm
    await bot.send_message(ADMIN_ID, f"Пользователь {uid} сообщает о покупке партнёра {pid}.\nЧтобы подтвердить и начислить cashback используйте:\n/confirm_purchase {uid} {pid} <amount>")
    await query.message.answer("Мы уведомили администратора. После проверки бонусы будут начислены.")

# Admin confirm purchase manually: /confirm_purchase <user_id> <partner_id> <amount>
@dp.message(Command("confirm_purchase"))
async def cmd_confirm_purchase(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("Нет доступа.")
        return
    parts = message.text.split()
    if len(parts) < 4:
        await message.reply("Использование: /confirm_purchase <user_id> <partner_id> <amount>")
        return
    try:
        uid = int(parts[1]); pid = int(parts[2]); amount = float(parts[3])
    except:
        await message.reply("Неверные параметры.")
        return
    res = await record_confirmed_purchase(uid, pid, amount, note=f"admin_confirmed_by_{message.from_user.id}", db_path=DB_PATH)
    await message.reply(f"Подтверждено. Начислено пользователю: {res['user_cashback']:.2f} ₽. Платформа: {res['platform_fee']:.2f} ₽")

# Withdraw: user creates payout request with /withdraw <amount> <method> <details>
@dp.message(Command("withdraw"))
async def cmd_withdraw(message: types.Message):
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.reply("Использование: /withdraw <amount> <method> <details>\nПример: /withdraw 500 qiwi +79991234567")
        return
    try:
        amount = float(parts[1])
    except:
        await message.reply("Неверная сумма.")
        return
    method = parts[2]
    details = parts[3]
    uid = message.from_user.id
    await create_payout_request(uid, amount, method, details, db_path=DB_PATH)
    await message.reply("Запрос на вывод создан. Админ свяжется с вами для подтверждения.", reply_markup=main_kb())

# Admin: list payout requests /payouts and mark paid /pay <id>
@dp.message(Command("payouts"))
async def cmd_list_payouts(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    rows = await list_payouts(DB_PATH)
    if not rows:
        await message.reply("Нет запросов на вывод.")
        return
    text = "Запросы на вывод:\n"
    for r in rows:
        pid, user_id, amount, method, details, status, created = r
        text += f"ID:{pid} User:{user_id} {amount}₽ {method} {status}\n"
    await message.reply(text)

@dp.message(Command("pay"))
async def cmd_pay(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.reply("Использование: /pay <payout_id> <paid|rejected>")
        return
    pid = int(parts[1]); status = parts[2]
    if status not in ("paid", "rejected", "approved"):
        await message.reply("Статус должен быть paid|rejected|approved")
        return
    await set_payout_status(pid, status, DB_PATH)
    await message.reply(f"Payout {pid} set to {status}")

# admin stats
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("Нет доступа.")
        return
    total = await total_users_count(DB_PATH)
    pstats = await partner_clicks_stats(DB_PATH)
    text = f"Admin stats\nUsers: {total}\n\nPartners:\n"
    for r in pstats:
        pid, name, cat, clicks = r
        text += f"- {name} ({cat}) — clicks: {clicks}\n"
    await message.reply(text)

# fallback help and menu
@dp.message()
async def fallback(message: types.Message):
    await message.answer("Используйте меню ниже.", reply_markup=main_kb())

# expose initializer for app.py
async def start_bg():
    await prepare()

# For external run (not used on render) - kept for local debug
if __name__ == "__main__":
    asyncio.run(prepare())
    # not starting polling in webhook mode