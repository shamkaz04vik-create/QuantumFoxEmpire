# db.py — асинхронная sqlite обёртка
import aiosqlite
import os
from config import DB_PATH

db: aiosqlite.Connection | None = None

async def init_db():
    global db
    # Убедимся, что директория для БД существует (если путь содержит папки)
    folder = os.path.dirname(DB_PATH)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    db = await aiosqlite.connect(DB_PATH)
    await db.execute("PRAGMA foreign_keys = ON;")
    # Создаём таблицы
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0,
            is_premium INTEGER DEFAULT 0,
            referred_by INTEGER,
            register_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_text TEXT,
            ai_text TEXT,
            date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    await db.commit()

async def ensure_db():
    """
    Если db ещё не инициирована — инициализируем.
    Это предотвращает ошибки 'NoneType' object has no attribute 'execute'
    если какой-то хендлер вызван до startup (на практике webhook стартует после startup).
    """
    global db
    if db is None:
        await init_db()

async def add_user(user_id: int, username: str, referred_by: int | None = None):
    await ensure_db()
    await db.execute(
        "INSERT OR IGNORE INTO users (user_id, username, referred_by) VALUES (?, ?, ?)",
        (user_id, username, referred_by)
    )
    await db.commit()

async def log_message(user_id: int, user_text: str, ai_text: str):
    await ensure_db()
    await db.execute(
        "INSERT INTO messages (user_id, user_text, ai_text) VALUES (?, ?, ?)",
        (user_id, user_text, ai_text)
    )
    await db.commit()

# Доп. функции, которые иногда используются ботом
async def set_premium(user_id: int, is_premium: bool):
    await ensure_db()
    await db.execute(
        "UPDATE users SET is_premium = ? WHERE user_id = ?",
        (1 if is_premium else 0, user_id)
    )
    await db.commit()

async def add_balance(user_id: int, amount: float):
    await ensure_db()
    await db.execute(
        "UPDATE users SET balance = balance + ? WHERE user_id = ?",
        (amount, user_id)
    )
    await db.commit()

async def close_db():
    global db
    if db:
        await db.close()
        db = None