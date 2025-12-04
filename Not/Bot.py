import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

TOKEN = "8456865406:AAGqqDLt4PpMf5QrDEPr7dDXymtTb_eN1_o"
ADMIN_ID = 7209803923

# =========================
# === БАЗА ДАННЫХ =========
# =========================

def db_connect():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        ref_by INTEGER,
        balance INTEGER DEFAULT 0
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS stats(
        service TEXT PRIMARY KEY,
        clicks INTEGER DEFAULT 0
    )""")
    conn.commit()
    return conn


conn = db_connect()
cur = conn.cursor()

# =========================
# === ГЛАВНОЕ МЕНЮ =========
# =========================

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💼 Услуги")],
        [
            KeyboardButton(text="💎 Полезные сервисы"),
            KeyboardButton(text="🎁 Реферальная система")
        ],
        [KeyboardButton(text="📊 Мой профиль")],
        [KeyboardButton(text="🛠 Админ-панель")],
    ],
    resize_keyboard=True
)

# ================================
# === ИНИЦИАЛИЗАЦИЯ БОТА =========
# ================================

bot = Bot(token=TOKEN)
dp = Dispatcher()

# =====================================
# === РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ =========
# =====================================

def register_user(user_id, ref_id=None):
    cur.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (user_id, ref_by) VALUES (?, ?)",
            (user_id, ref_id)
        )
        conn.commit()

        if ref_id:
            cur.execute("UPDATE users SET balance = balance + 20 WHERE user_id = ?", (ref_id,))
            cur.execute("UPDATE users SET balance = balance + 10 WHERE user_id = ?", (user_id,))
            conn.commit()


# ================================
# === КОМАНДА /START =============
# ================================

@dp.message(Command("start"))
async def start_cmd(message: Message):
    user_id = message.from_user.id
    args = message.text.split()

    ref = None
    if len(args) > 1 and args[1].startswith("ref"):
        ref = int(args[1].replace("ref", ""))

    register_user(user_id, ref)

    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n"
        f"Добро пожаловать в QuantumFoxEmpire.\n\n"
        f"Выберите действие:",
        reply_markup=main_menu
    )

# ===========================================
# === ОБРАБОТКА ПУНКТОВ МЕНЮ =================
# ===========================================

@dp.message(F.text == "📊 Мой профиль")
async def my_profile(message: Message):
    user_id = message.from_user.id
    cur.execute("SELECT balance, ref_by FROM users WHERE user_id = ?", (user_id,))
    data = cur.fetchone()

    if data:
        balance, ref_by = data
    else:
        balance, ref_by = 0, None

    await message.answer(
        f"👤 Ваш профиль\n"
        f"ID: {user_id}\n"
        f"💰 Баланс: {balance}₽\n"
        f"👥 Кто пригласил: {ref_by if ref_by else 'Никто'}"
    )

# =============================
# === РЕФЕРАЛЬНАЯ СИСТЕМА =====
# =============================

@dp.message(F.text == "🎁 Реферальная система")
async def referral_system(message: Message):
    user_id = message.from_user.id
    link = f"https://t.me/QuantumFoxEmpire_bot?start=ref{user_id}"

    await message.answer(
        f"🎁 Реферальная программа\n\n"
        f"🔗 Ваша ссылка:\n{link}\n\n"
        f"За каждого приглашённого:\n"
        f"— Вы: +20₽\n"
        f"— Друг: +10₽"
    )

# =============================
# === ПОЛЕЗНЫЕ СЕРВИСЫ =========
# =============================

@dp.message(F.text == "💎 Полезные сервисы")
async def useful_services(message: Message):
    menu = (
        "💎 Полезные сервисы:\n\n"
        "1️⃣ VPN сервисы\n"
        "2️⃣ AI подписки\n"
        "3️⃣ Финансовые сервисы\n"
        "4️⃣ Telegram инструменты\n\n"
        "Напиши цифру категории:"
    )
    await message.answer(menu)

@dp.message(F.text.in_(["1", "1️⃣"]))
async def vpn_list(message: Message):
    await message.answer(
        "🌐 VPN сервисы:\n\n"
        "🔹 Surfshark — https://track.surfshark.com\n"
        "🔹 NordVPN — https://nordvpn.com\n"
        "🔹 AtlasVPN — https://atlasvpn.com\n"
    )

@dp.message(F.text.in_(["2", "2️⃣"]))
async def ai_list(message: Message):
    await message.answer(
        "🤖 AI подписки:\n\n"
        "🔹 ChatGPT Plus — https://openai.com\n"
        "🔹 Midjourney — https://www.midjourney.com\n"
        "🔹 Notion AI — https://notion.so\n"
    )

@dp.message(F.text.in_(["3", "3️⃣"]))
async def finance_list(message: Message):
    await message.answer(
        "💵 Финансы:\n\n"
        "🔹 LetyShops — https://letyshops.com\n"
        "🔹 Backit — https://backit.me\n"
    )

@dp.message(F.text.in_(["4", "4️⃣"]))
async def tg_tools(message: Message):
    await message.answer(
        "📱 Telegram инструменты:\n\n"
        "🔹 Telega.io — https://telega.io\n"
        "🔹 PosterBot — https://posterbot.ru\n"
    )

# =============================
# === АДМИН-КОМАНДЫ ===========
# =============================

@dp.message(F.text == "🛠 Админ-панель")
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ У вас нет доступа.")
    
    await message.answer(
        "🛠 Админ-панель\n\n"
        "1 — Статистика кликов\n"
        "2 — Список пользователей\n"
    )

@dp.message(F.text == "1")
async def admin_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    cur.execute("SELECT service, clicks FROM stats")
    rows = cur.fetchall()

    text = "📊 Статистика кликов:\n\n"
    for service, clicks in rows:
        text += f"{service}: {clicks}\n"

    await message.answer(text)

@dp.message(F.text == "2")
async def admin_users(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]

    await message.answer(f"👥 Пользователей в базе: {total}")

# =============================
# === ЗАПУСК ===================
# =============================

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())