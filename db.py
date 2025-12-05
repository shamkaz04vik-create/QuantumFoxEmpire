import aiosqlite
from config import DB_PATH

db = None

async def init_db():
    global db

    if db is not None:
        return

    print("▶ CONNECTING TO DB:", DB_PATH)
    db = await aiosqlite.connect(DB_PATH)
    await db.execute("PRAGMA foreign_keys = ON;")

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
    print("▶ DB READY")


async def add_user(user_id: int, username: str):
    await db.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username)
    )
    await db.commit()


async def log_message(user_id: int, user_text: str, ai_text: str):
    await db.execute(
        "INSERT INTO messages (user_id, user_text, ai_text) VALUES (?, ?, ?)",
        (user_id, user_text, ai_text)
    )
    await db.commit()


async def set_premium(user_id: int, is_premium: bool):
    await db.execute(
        "UPDATE users SET is_premium = ? WHERE user_id = ?",
        (1 if is_premium else 0, user_id)
    )
    await db.commit()


async def add_balance(user_id: int, amount: float):
    await db.execute(
        "UPDATE users SET balance = balance + ? WHERE user_id = ?",
        (amount, user_id)
    )
    await db.commit()