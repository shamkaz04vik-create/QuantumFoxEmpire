# Bot.py — Полный код: меню, каталог услуг, рефералы (как было), + Полезные сервисы (партнёрки) с трекингом кликов
import asyncio
import os
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

# ========== Настройки ==========
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7209803923  # твой Telegram ID
BOT_USERNAME = "QuantumFoxEmpire_bot"  # имя бота без @
DB_PATH = os.getenv("DB_PATH", "data.db")

# бонусы — оставить как есть или менять
NEW_USER_BONUS = 50.0
REFERRER_BONUS = 80.0

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ========== UI (клавиатуры) ==========
def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="💼 Услуги")
    kb.button(text="💰 Заработок")
    kb.button(text="👤 Профиль")
    kb.button(text="📞 Поддержка")
    kb.button(text="💎 Полезные сервисы")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def services_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="🧑‍💻 Создание ботов")
    kb.button(text="🎨 Дизайн")
    kb.button(text="📢 Реклама и продвижение")
    kb.button(text="📱 Создание сайтов")
    kb.button(text="🔙 Назад")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def partners_categories_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="1️⃣ VPN")
    kb.button(text="2️⃣ AI-подписки")
    kb.button(text="3️⃣ Кэшбек / Финансы")
    kb.button(text="4️⃣ Telegram-инструменты")
    kb.button(text="🔙 Назад")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def admin_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="📢 Рассылка")
    kb.button(text="📊 Статистика")
    kb.button(text="🔙 Назад")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

# ========== Партнёры — начальный набор (редактируй ссылки и комиссии) ==========
# partner records: (name, url, category, commission_percent)
INITIAL_PARTNERS = [
    ("Surfshark VPN", "https://surfshark.example/ref=yourcode", "vpn", 40),
    ("NordVPN", "https://nordvpn.example/ref=yourcode", "vpn", 35),
    ("AI Assistant Pro", "https://aiassist.example/ref=yourcode", "ai", 30),
    ("Midjourney Plus", "https://midjourney.example/ref=yourcode", "ai", 25),
    ("LetyShops Cashback", "https://lety.example/ref=yourcode", "cashback", 20),
    ("Backit Finance", "https://backit.example/ref=yourcode", "cashback", 15),
    ("TG Scheduler", "https://tgscheduler.example/ref=yourcode", "tg_tools", 40),
    ("AutoPoster Pro", "https://autoposter.example/ref=yourcode", "tg_tools", 35),
]

# ========== БД: создание таблиц и утилиты ==========
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER UNIQUE,
                ref_by INTEGER DEFAULT NULL,
                balance REAL DEFAULT 0,
                invited_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER,
                amount REAL,
                type TEXT,
                note TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS partners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                url TEXT,
                category TEXT,
                commission_percent REAL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS partner_clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_id INTEGER,
                tg_id INTEGER,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.commit()

        # insert initial partners if table empty
        cur = await db.execute("SELECT COUNT(*) FROM partners")
        count = (await cur.fetchone())[0]
        if count == 0:
            for p in INITIAL_PARTNERS:
                await db.execute(
                    "INSERT INTO partners (name, url, category, commission_percent) VALUES (?, ?, ?, ?)",
                    (p[0], p[1], p[2], p[3])
                )
            await db.commit()

# ===== user helpers (same as раньше) =====
async def get_user_by_tg(tg_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, tg_id, ref_by, balance, invited_count FROM users WHERE tg_id = ?", (tg_id,))
        return await cur.fetchone()

async def create_user(tg_id, ref_by=None):
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("INSERT INTO users (tg_id, ref_by, balance) VALUES (?, ?, ?)", (tg_id, ref_by, 0.0))
            await db.commit()
        except Exception:
            return
        cur = await db.execute("SELECT id, tg_id, ref_by, balance, invited_count FROM users WHERE tg_id = ?", (tg_id,))
        return await cur.fetchone()

async def add_balance(tg_id, amount, tx_type="credit", note=""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE tg_id = ?", (amount, tg_id))
        await db.execute("INSERT INTO transactions (tg_id, amount, type, note) VALUES (?, ?, ?, ?)", (tg_id, amount, tx_type, note))
        await db.commit()

async def inc_invited(ref_tg_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET invited_count = invited_count + 1 WHERE tg_id = ?", (ref_tg_id,))
        await db.commit()

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        total_users = (await cur.fetchone())[0]
        cur = await db.execute("SELECT IFNULL(SUM(balance),0) FROM users")
        total_balance = (await cur.fetchone())[0]
        return total_users, total_balance

# ===== partner helpers =====
async def list_partners_by_category(category):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, name FROM partners WHERE category = ? ORDER BY id", (category,))
        return await cur.fetchall()

async def get_partner(partner_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, name, url, category, commission_percent FROM partners WHERE id = ?", (partner_id,))
        return await cur.fetchone()

async def record_partner_click(partner_id, tg_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO partner_clicks (partner_id, tg_id) VALUES (?, ?)", (partner_id, tg_id))
        await db.commit()

async def get_partner_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            SELECT p.id, p.name, p.category, p.commission_percent, COUNT(pc.id) as clicks
            FROM partners p
            LEFT JOIN partner_clicks pc ON pc.partner_id = p.id
            GROUP BY p.id ORDER BY clicks DESC
        """)
        return await cur.fetchall()

# ========== /start (реферальная логика, регистрация) ==========
@dp.message(CommandStart())
async def on_start(message: types.Message):
    payload = message.get_args() or ""
    tg_id = message.from_user.id
    await init_db()
    user = await get_user_by_tg(tg_id)
    if user:
        await message.answer("С возвращением!", reply_markup=main_menu())
        return

    ref_by = None
    if payload.startswith("ref"):
        try:
            ref_candidate = int(payload[3:])
            if ref_candidate != tg_id:
                ref_row = await get_user_by_tg(ref_candidate)
                if ref_row:
                    ref_by = ref_candidate
        except Exception:
            ref_by = None

    await create_user(tg_id, ref_by=ref_by)

    if ref_by:
        await add_balance(tg_id, NEW_USER_BONUS, tx_type="bonus", note="new_user_bonus")
        await add_balance(ref_by, REFERRER_BONUS, tx_type="ref_bonus", note=f"referral_of_{tg_id}")
        await inc_invited(ref_by)
        await message.answer(f"Спасибо за регистрацию! Ты получил бонус {NEW_USER_BONUS} ₽. Тот, кто пригласил — получил {REFERRER_BONUS} ₽.", reply_markup=main_menu())
    else:
        await add_balance(tg_id, 0.0, tx_type="system", note="created_without_bonus")
        await message.answer("Добро пожаловать! Используй меню для работы с ботом.", reply_markup=main_menu())

# ========== Обработка текстовых кнопок ==========
@dp.message()
async def menu_handler(message: types.Message):
    text = message.text
    tg_id = message.from_user.id

    # --- Услуги ---
    if text == "💼 Услуги":
        await message.answer("Выберите услугу:", reply_markup=services_menu())
        return

    if text == "🧑‍💻 Создание ботов":
        await message.answer("🧑‍💻 *Создание Telegram-ботов*\nЦена: от 5000 ₽\n\nОпишите задачу, и мы обсудим!", parse_mode="Markdown")
        return
    if text == "🎨 Дизайн":
        await message.answer("🎨 *Дизайн (логотипы, баннеры, обложки)*\nЦена: от 1000 ₽", parse_mode="Markdown")
        return
    if text == "📢 Реклама и продвижение":
        await message.answer("📢 *Продвижение Telegram-каналов*\nЦена: индивидуально.", parse_mode="Markdown")
        return
    if text == "📱 Создание сайтов":
        await message.answer("📱 *Создание сайтов под ключ*\nЦена: от 10 000 ₽", parse_mode="Markdown")
        return
    if text == "🔙 Назад":
        await message.answer("Главное меню:", reply_markup=main_menu())
        return

    # --- Заработок (рефералы) ---
    if text == "💰 Заработок":
        user = await get_user_by_tg(tg_id)
        if not user:
            await message.answer("Сначала зарегистрируйтесь через /start")
            return
        _, _, _, balance, invited_count = user
        ref_link = f"https://t.me/{BOT_USERNAME}?start=ref{tg_id}"
        await message.answer(f"💰 Ваша реферальная ссылка:\n{ref_link}\n\nПриглашено: {invited_count} чел.\nБаланс: {balance:.2f} ₽", reply_markup=main_menu())
        return

    # --- Профиль ---
    if text == "👤 Профиль":
        user = await get_user_by_tg(tg_id)
        if not user:
            await message.answer("Сначала зарегистрируйтесь через /start")
            return
        _, _, _, balance, invited_count = user
        await message.answer(f"👤 Ваш Telegram ID: {tg_id}\nПриглашено: {invited_count}\nБаланс: {balance:.2f} ₽", reply_markup=main_menu())
        return

    # --- Поддержка ---
    if text == "📞 Поддержка":
        await message.answer("Напишите нам: @your_support", reply_markup=main_menu())
        return

    # --- Полезные сервисы (партнёрки) ---
    if text == "💎 Полезные сервисы":
        await message.answer("Выберите категорию:", reply_markup=partners_categories_menu())
        return

    # Categories
    if text == "1️⃣ VPN":
        await send_partners_list(message, "vpn")
        return
    if text == "2️⃣ AI-подписки":
        await send_partners_list(message, "ai")
        return
    if text == "3️⃣ Кэшбек / Финансы":
        await send_partners_list(message, "cashback")
        return
    if text == "4️⃣ Telegram-инструменты":
        await send_partners_list(message, "tg_tools")
        return
    if text == "🔙 Назад":
        await message.answer("Главное меню:", reply_markup=main_menu())
        return

    # --- Админские кнопки ---
    if text == "🛠 Админ" and tg_id == ADMIN_ID:
        await message.answer("Админ меню:", reply_markup=admin_menu())
        return
    if text == "📢 Рассылка" and tg_id == ADMIN_ID:
        await message.answer("Введите текст рассылки (скрипт рассылки будет добавлен позже).")
        return
    if text == "📊 Статистика" and tg_id == ADMIN_ID:
        total_users, total_balance = await get_stats()
        partner_stats = await get_partner_stats()
        stats_text = f"📊 Всего пользователей: {total_users}\n💰 Суммарный баланс: {total_balance:.2f} ₽\n\nПартнёрская статистика (клики):\n"
        for p in partner_stats:
            pid, name, cat, comm, clicks = p
            stats_text += f"- {name} ({cat}) — кликов: {clicks}, комиссия: {comm}%\n"
        await message.answer(stats_text)
        return

    # fallback
    await message.answer("Не понял команду. Используйте меню.", reply_markup=main_menu())

# ========== Функции показа партнёров и обработка кликов ==========
async def send_partners_list(message: types.Message, category: str):
    rows = await list_partners_by_category(category)
    if not rows:
        await message.answer("Партнёров в этой категории нет.", reply_markup=main_menu())
        return
    for row in rows:
        partner_id, name = row
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Перейти и получить скидку", callback_data=f"open_partner:{partner_id}")],
            [InlineKeyboardButton(text="Подробнее", callback_data=f"info_partner:{partner_id}")]
        ])
        await message.answer(f"🔹 {name}", reply_markup=kb)

# Callback: показать info (описание — сейчас только имя + комиссия)
@dp.callback_query(lambda c: c.data and c.data.startswith("info_partner:"))
async def callback_info_partner(query: types.CallbackQuery):
    await query.answer()  # acknowledge
    partner_id = int(query.data.split(":")[1])
    p = await get_partner(partner_id)
    if not p:
        await query.message.answer("Партнёр не найден.")
        return
    pid, name, url, category, comm = p
    text = f"🔸 {name}\nКатегория: {category}\nКомиссия: {comm}%\nСсылка будет доступна после нажатия «Перейти»."
    await query.message.answer(text)

# Callback: открыть партнёрскую ссылку — записываем клик, потом посылаем кнопку c URL
@dp.callback_query(lambda c: c.data and c.data.startswith("open_partner:"))
async def callback_open_partner(query: types.CallbackQuery):
    await query.answer()  # acknowledge to remove 'loading'
    partner_id = int(query.data.split(":")[1])
    p = await get_partner(partner_id)
    if not p:
        await query.message.answer("Партнёр не найден.")
        return
    pid, name, url, category, comm = p
    # record click
    try:
        await record_partner_click(pid, query.from_user.id)
    except Exception:
        pass
    # send button with actual URL
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Перейти к {name}", url=url)]
    ])
    await query.message.answer(f"Вы переходите на: {name}\nНажмите кнопку ниже для перехода.", reply_markup=kb)

# ========== Запуск ==========
async def main():
    await init_db()
    # nothing else to init
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())