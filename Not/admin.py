# admin.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from config import ADMIN_IDS
from db import get_stats, get_user, add_event, set_vip

router = Router()

def is_admin(user_id: int):
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def admin_main(m: Message):
    if not is_admin(m.from_user.id):
        await m.answer("Нет доступа.")
        return
    await m.answer("Панель админа:\n/stat - статистика\n/addvip <id> <days> - дать vip")

@router.message(Command("stat"))
async def cmd_stats(m: Message):
    if not is_admin(m.from_user.id):
        await m.answer("Нет доступа.")
        return
    s = await get_stats()
    await m.answer(f"Users: {s['users']}\nEvents: {s['events']}")

@router.message(Command("addvip"))
async def cmd_addvip(m: Message):
    if not is_admin(m.from_user.id):
        await m.answer("Нет доступа.")
        return
    parts = m.text.split()
    if len(parts) < 3:
        await m.answer("Использование: /addvip <user_id> <days>")
        return
    try:
        uid = int(parts[1])
        days = int(parts[2])
    except:
        await m.answer("Неверные параметры")
        return
    import time
    until = int(time.time()) + days*24*3600
    await set_vip(uid, until)
    await add_event(m.from_user.id, "admin_addvip", f"{uid}:{days}")
    await m.answer(f"VIP добавлен пользователю {uid} на {days} дней")