# Bot.py — полный рабочий бот с базой (aiosqlite), реферами и VPN-партнёрками
import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# ---------- Настройки (твой токен уже вставлен) ----------
TOKEN = "8456865406:AAGqqDLt4PpMf5QrDEPr7dDXymtTb_eN1_o"
ADMIN_ID = 7209803923  # твой Telegram ID (убедись, что верный)

DB_PATH = "database.db"

# ---------- Инициализация бота ----------
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------- Клавиатуры ----------
def main_menu_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("🎛 Профиль")],
        [KeyboardButton("💰 Заработок"), KeyboardButton("🧰 Инструменты")],
        [KeyboardButton("💼 Услуги"), KeyboardButton("🔒 VPN Партнёрки")],
        [KeyboardButton("🧑‍🤝‍🧑 Реферальная система")]
    ], resize_keyboard=True)
    return kb

def back_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton("🔙 Назад")]], resize_keyboard=True)

def vpn_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("⚡ Молния VPN")],
        [KeyboardButton("🛡 Kovalenko VPN")],
        [KeyboardButton("🔙 Назад")]
    ], resize_keyboard=True)

# ---------- SQL: инициализация БД ----------
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                referrer INTEGER,
                balance REAL DEFAULT 0,
                joined_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS partners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                url_template TEXT,
                category TEXT,
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS partner_clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_id INTEGER,
                user_id INTEGER,
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                type TEXT,
                note TEXT,
                created_at TEXT
            )
        """)
        await db.commit()

        # вставим две партнёрки, если таблица пустая
        cur = await db.execute("SELECT COUNT(*) FROM partners")
        row = await cur.fetchone()
        count = row[0] if row else 0
        if count == 0:
            partners = [
                # url_template должен содержать место для subid / user — мы используем {user}
                ("Molniya VPN", "https://t.me/molniya_vpn_bot?start=john0_8_{user}", "vpn"),
                ("Kovalenko VPN", "https://t.me/Kovalenkovpn_bot?start=john0_8_{user}", "vpn"),
            ]
            for name, url, cat in partners:
                await db.execute(
                    "INSERT INTO partners (name, url_template, category, created_at) VALUES (?, ?, ?, ?)",
                    (name, url, cat, datetime.utcnow().isoformat())
                )
            await db.commit()

# ---------- Утилиты работы с БД ----------
async def add_user_if_not_exists(user: types.User, ref: int | None = None):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user.id,))
        exists = await cur.fetchone()
        if exists:
            return False
        await db.execute(
            "INSERT INTO users (user_id, username, first_name, referrer, joined_at) VALUES (?, ?, ?, ?, ?)",
            (user.id, user.username or "", user.first_name or "", ref, datetime.utcnow().isoformat())
        )
        if ref:
            # при регистрации реферал получает бонус (примерно)
            await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (20.0, ref))
            await db.execute("INSERT INTO transactions (user_id, amount, type, note, created_at) VALUES (?, ?, ?, ?, ?)",
                             (ref, 20.0, "ref_bonus", f"bonus_for_ref_{user.id}", datetime.utcnow().isoformat()))
            # и новичку даём небольшой бонус
            await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (10.0, user.id))
            await db.execute("INSERT INTO transactions (user_id, amount, type, note, created_at) VALUES (?, ?, ?, ?, ?)",
                             (user.id, 10.0, "new_user_bonus", "welcome_bonus", datetime.utcnow().isoformat()))
        await db.commit()
        return True

async def get_user_stats(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT balance, referrer FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        if not row:
            return None
        balance, referrer = row
        cur = await db.execute("SELECT COUNT(*) FROM users WHERE referrer = ?", (user_id,))
        refs = (await cur.fetchone())[0]
        return {"balance": balance, "referrer": referrer, "refs": refs}

async def list_partners():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, name, url_template, category FROM partners ORDER BY id")
        return await cur.fetchall()

async def get_partner(pid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, name, url_template FROM partners WHERE id = ?", (pid,))
        return await cur.fetchone()

async def record_partner_click(partner_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO partner_clicks (partner_id, user_id, created_at) VALUES (?, ?, ?)",
                         (partner_id, user_id, datetime.utcnow().isoformat()))
        await db.commit()

async def partner_clicks_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            SELECT p.id, p.name, p.category, COUNT(pc.id) as clicks
            FROM partners p
            LEFT JOIN partner_clicks pc ON pc.partner_id = p.id
            GROUP BY p.id ORDER BY clicks DESC
        """)
        return await cur.fetchall()

async def total_users_count():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        return (await cur.fetchone())[0]

# ---------- /start обработчик (реф-параметр поддерживается) ----------
@dp.message(CommandStart())
async def on_start(message: types.Message):
    # payload может быть: "ref<id>" или "john0_8_<user>" или пуст
    args = message.get_args() or ""
    ref = None

    # поддержка двух схем: /start ref12345  или /start john0_8_12345
    if args:
        if args.startswith("ref"):
            try:
                ref = int(args[3:])
            except Exception:
                ref = None
        else:
            # если payload содержит подстроку с числом в конце, возьмём последний int
            try:
                parts = args.split("_")
                possible = parts[-1]
                ref = int(possible)
            except Exception:
                ref = None

    created = await add_user_if_not_exists(message.from_user, ref)
    if created and ref:
        await message.answer("Спасибо за регистрацию! Бонусы начислены.", reply_markup=main_menu_kb())
    else:
        await message.answer("Добро пожаловать обратно!", reply_markup=main_menu_kb())

# ---------- Меню: профиль ----------
@dp.message(lambda msg: msg.text == "🎛 Профиль")
async def handle_profile(message: types.Message):
    uid = message.from_user.id
    stats = await get_user_stats(uid)
    if not stats:
        await message.answer("Пользователь не найден. Нажми /start", reply_markup=main_menu_kb())
        return
    text = (f"👤 Профиль\n\n"
            f"ID: `{uid}`\n"
            f"Имя: {message.from_user.full_name}\n"
            f"Баланс: {stats['balance']:.2f} ₽\n"
            f"Приглашён: {stats['refs']} чел.\n")
    await message.answer(text, parse_mode="Markdown", reply_markup=back_kb())

# ---------- Меню: рефералка ----------
@dp.message(lambda msg: msg.text == "🧑‍🤝‍🧑 Реферальная система")
async def handle_referral(message: types.Message):
    me = await bot.get_me()
    ref_link = f"https://t.me/{me.username}?start=john0_8_{message.from_user.id}"
    text = ("🔁 Реферальная система\n\n"
            "Приглашай людей и получай бонусы!\n"
            f"Твоя реферальная ссылка:\n{ref_link}\n\n"
            "Каждый приглашённый даёт ему +10₽, тебе +20₽ (пример).\n")
    await message.answer(text, reply_markup=back_kb())

# ---------- Меню: услуги ----------
@dp.message(lambda msg: msg.text == "💼 Услуги")
async def handle_services(message: types.Message):
    text = (
        "💼 Наши услуги:\n\n"
        "🤖 Создание ботов — от 5000 ₽\n"
        "🎨 Дизайн — от 1000 ₽\n"
        "📣 Продвижение каналов — по тарифам\n"
        "🌐 Сайты — от 7000 ₽\n\n"
        "Напишите, какая услуга нужна, и мы ответим."
    )
    await message.answer(text, reply_markup=back_kb())

# ---------- Меню: инструменты ----------
@dp.message(lambda msg: msg.text == "🧰 Инструменты")
async def handle_tools(message: types.Message):
    text = ("🧰 Инструменты:\n\n"
            "— Генерация текста (скоро)\n"
            "— Автоответы (скоро)\n"
            "— Аналитика (скоро)\n")
    await message.answer(text, reply_markup=back_kb())

# ---------- Меню: VPN партнерки (кнопки) ----------
@dp.message(lambda msg: msg.text == "🔒 VPN Партнёрки")
async def handle_vpn_menu(message: types.Message):
    parts = await list_partners()
    if not parts:
        await message.answer("Партнёры не найдены.", reply_markup=back_kb())
        return
    # покажем список партнёров с кнопками
    for p in parts:
        pid, name, url_template, category = p
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Перейти по ссылке", callback_data=f"open_partner:{pid}")],
            [InlineKeyboardButton(text="Подробнее", callback_data=f"info_partner:{pid}")]
        ])
        await message.answer(f"🔹 {name}", reply_markup=kb)

# ---------- Callback: подробности партнёра ----------
@dp.callback_query(lambda c: c.data and c.data.startswith("info_partner:"))
async def cb_info_partner(query: types.CallbackQuery):
    await query.answer()
    pid = int(query.data.split(":")[1])
    p = await get_partner(pid)
    if not p:
        await query.message.answer("Партнёр не найден.")
        return
    _, name, url_template = p
    text = f"🔸 {name}\nСсылка будет с подстановкой вашего ID при переходе."
    await query.message.answer(text)

# ---------- Callback: открыть партнёрскую ссылку (запись клика + выдача URL) ----------
@dp.callback_query(lambda c: c.data and c.data.startswith("open_partner:"))
async def cb_open_partner(query: types.CallbackQuery):
    await query.answer()
    pid = int(query.data.split(":")[1])
    p = await get_partner(pid)
    if not p:
        await query.message.answer("Партнёр не найден.")
        return
    _, name, url_template = p
    uid = query.from_user.id
    # записать клик
    try:
        await record_partner_click(pid, uid)
    except Exception:
        pass
    # подставить user
    url = url_template.format(user=uid)
    # отправить как кнопку (редирект)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Перейти к {name}", url=url)]
    ])
    await query.message.answer(f"Вы переходите на {name}. Нажмите кнопку ниже:", reply_markup=kb)

# ---------- Админ-панель (кнопка в меню можно вызвать через текст) ----------
@dp.message(lambda msg: msg.text == "💰 Заработок")
async def handle_earning(message: types.Message):
    text = ("💰 Возможности заработка:\n\n"
            "— Реферальная система\n"
            "— Партнёрские программы (VPN и др.)\n"
            "— Продажа услуг\n\n"
            "Админ-панель доступна по команде /admin (только для админа).")
    await message.answer(text, reply_markup=back_kb())

@dp.message(commands=["admin"])
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет доступа.")
        return
    # собрать статистику
    total = await total_users_count()
    pstats = await partner_clicks_stats()
    text = f"🔐 Admin панель\n\nВсего пользователей: {total}\n\nПартнёрская статистика:\n"
    for row in pstats:
        pid, name, cat, clicks = row
        text += f"- {name} ({cat}) — кликов: {clicks}\n"
    await message.answer(text)

# ---------- Вспомогательные команды ----------
@dp.message(lambda msg: msg.text == "🔙 Назад")
async def back_to_main(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_menu_kb())

@dp.message(commands=["stats"])
async def cmd_stats(message: types.Message):
    # личная статистика
    uid = message.from_user.id
    stats = await get_user_stats(uid)
    if not stats:
        await message.answer("Вы не зарегистрированы. Нажмите /start")
        return
    await message.answer(f"Баланс: {stats['balance']:.2f} ₽\nПриглашено: {stats['refs']}")

# ---------- Запуск бота ----------
async def main():
    await init_db()
    print("DB initialized. Bot start polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())