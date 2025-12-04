# admin.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from db import total_users, list_partners
from db import get_user
from payments import confirm_manual_payment
from config import ADMIN_ID
import csv
import aiosqlite

router = Router()

def is_admin(uid):
    return uid == ADMIN_ID

@router.message(Command("admin"))
async def cmd_admin(m: Message):
    if not is_admin(m.from_user.id):
        return await m.answer("Нет доступа.")
    await m.answer("/stats - показать статистику\n/confirm_payment <user_id> <amount> - подтвердить платёж\n/export_users - выгрузить users.csv")

@router.message(Command("stats"))
async def cmd_stats(m: Message):
    if not is_admin(m.from_user.id):
        return
    u = await total_users()
    parts = await list_partners()
    text = f"Пользователей: {u}\nПартнёров: {len(parts)}"
    await m.answer(text)

@router.message(Command("confirm_payment"))
async def cmd_confirm_payment(m: Message):
    if not is_admin(m.from_user.id):
        return
    parts = m.text.split()
    if len(parts) < 3:
        return await m.answer("Использование: /confirm_payment <user_id> <amount>")
    try:
        uid = int(parts[1]); amount = float(parts[2])
    except:
        return await m.answer("Неверные параметры.")
    res = await confirm_manual_payment(uid, amount, m.from_user.id)
    await m.answer(f"Платёж подтверждён: {res}")

@router.message(Command("export_users"))
async def cmd_export_users(m: Message):
    if not is_admin(m.from_user.id):
        return
    # export users to CSV
    import io, aiosqlite
    conn = await aiosqlite.connect('/data/database.db')
    cur = await conn.execute("SELECT user_id, username, first_name, referrer, balance, vip_until FROM users")
    rows = await cur.fetchall()
    await conn.close()
    out = "user_id,username,first_name,referrer,balance,vip_until\n"
    for r in rows:
        out += ",".join([str(i) if i is not None else "" for i in r]) + "\n"
    await m.answer_document(("users.csv", out.encode('utf-8')))
