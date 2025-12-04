# Bot.py — полный рабочий код с реферальной системой (aiogram 3.x + aiosqlite)
import asyncio
import os
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# ---------- Настройки ----------
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7209803923  # твой Telegram ID
BOT_USERNAME = "QuantumFoxEmpire_bot"  # username без @ — использую в ссылках
DB_PATH = os.getenv("DB_PATH", "data.db")
# бонусы (можешь менять)
NEW_USER_BONUS = 10.0
REFERRER_BONUS = 20.0

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------- Клавиатуры ----------
def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="💼 Услуги")
    kb.button(text="💰 Заработок")
    kb.button(text="👤 Профиль")
    kb.button(text="📞 Поддержка")
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

def admin_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="📢 Рассылка")
    kb.button(text="📊 Статистика")
    kb.button(text="🔙 Назад")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

# ---------- База данных ----------
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
        await db.commit()

async def get_user_by_tg(tg_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, tg_id, ref_by, balance, invited_count FROM users WHERE tg_id = ?", (tg_id,))
        row = await cur.fetchone()
        return row

async def create_user(tg_id, ref_by=None):
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("INSERT INTO users (tg_id, ref_by, balance) VALUES (?, ?, ?)",
                             (tg_id, ref_by, 0.0))
            await db.commit()
        except Exception:
            return
        # fetch inserted
        cur = await db.execute("SELECT id, tg_id, ref_by, balance, invited_count FROM users WHERE tg_id = ?", (tg_id,))
        user = await cur.fetchone()
        return user

async def add_balance(tg_id, amount, tx_type="credit", note=""):
    async with aiosqlite.connect(DB_PATH) as db:
        # update balance
        await db.execute("UPDATE users SET balance = balance + ? WHERE tg_id = ?", (amount, tg_id))
        await db.execute("INSERT INTO transactions (tg_id, amount, type, note) VALUES (?, ?, ?, ?)",
                         (tg_id, amount, tx_type, note))
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

# ---------- Обработка /start (с реферальным параметром) ----------
@dp.message(CommandStart())
async def on_start(message: types.Message):
    # payload: e.g. "ref123456789"
    payload = message.get_args() or ""
    tg_id = message.from_user.id

    # инициализация БД если нужно
    await init_db()

    user = await get_user_by_tg(tg_id)
    if user:
        # уже зарегистрирован
        await message.answer("С возвращением!", reply_markup=main_menu())
        return

    # Обрабатываем ссылку реферала
    ref_by = None
    if payload.startswith("ref"):
        try:
            ref_candidate = int(payload[3:])
            # защита от само-реферала
            if ref_candidate != tg_id:
                # проверим, существует ли реферер
                ref_row = await get_user_by_tg(ref_candidate)
                if ref_row:
                    ref_by = ref_candidate
        except Exception:
            ref_by = None

    # Создаём пользователя
    await create_user(tg_id, ref_by=ref_by)

    # Если есть реферер — начисляем бонусы
    if ref_by:
        # бонус новому пользователю
        await add_balance(tg_id, NEW_USER_BONUS, tx_type="bonus", note="new_user_bonus")
        # бонус рефереру
        await add_balance(ref_by, REFERRER_BONUS, tx_type="ref_bonus", note=f"referral_of_{tg_id}")
        # увеличиваем счётчик приглашённых
        await inc_invited(ref_by)
        await message.answer(
            f"Спасибо за регистрацию! Ты получил бонус {NEW_USER_BONUS} ₽. "
            f"Тот, кто пригласил — получил {REFERRER_BONUS} ₽.",
            reply_markup=main_menu()
        )
    else:
        # без реферала — просто стартовый привет
        await add_balance(tg_id, 0.0, tx_type="system", note="created_without_bonus")
        await message.answer("Добро пожаловать! Используй меню для работы с ботом.", reply_markup=main_menu())

# ---------- Основное меню и обработка кнопок ----------
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
        # покажем реферальную ссылку и баланс
        user = await get_user_by_tg(tg_id)
        if not user:
            await message.answer("Сначала зарегистрируйтесь через /start")
            return
        _, _, _, balance, invited_count = user
        # формируем реферальную ссылку
        ref_link = f"https://t.me/{BOT_USERNAME}?start=ref{tg_id}"
        await message.answer(
            f"💰 Ваша реферальная ссылка:\n{ref_link}\n\n"
            f"Приглашено: {invited_count} чел.\n"
            f"Баланс: {balance:.2f} ₽",
            reply_markup=main_menu()
        )
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

    # --- Админские функции ---
    if text == "🛠 Админ" and tg_id == ADMIN_ID:
        await message.answer("Админ меню:", reply_markup=admin_menu())
        return

    if text == "📢 Рассылка" and tg_id == ADMIN_ID:
        await message.answer("Введите текст рассылки (скрипт рассылки будет добавлен позже).")
        return

    if text == "📊 Статистика" and tg_id == ADMIN_ID:
        total_users, total_balance = await get_stats()
        await message.answer(f"📊 Всего пользователей: {total_users}\n💰 Суммарный баланс: {total_balance:.2f} ₽")
        return

    # --- fallback ---
    await message.answer("Не понял команду. Используйте меню.", reply_markup=main_menu())

# ---------- Запуск ----------
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())