import aiosqlite
from config import DB_PATH

db: aiosqlite.Connection = None


# =====================================================
# ИНИЦИАЛИЗАЦИЯ БД (единое соединение)
# =====================================================
async def init_db():
    global db

    db = await aiosqlite.connect(DB_PATH)
    await db.execute("PRAGMA foreign_keys = ON;")   # важнейшая строка

    # Таблица пользователей
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

    # Индексы
    await db.execute("CREATE INDEX IF NOT EXISTS idx_user_ref ON users(referred_by);")

    # Таблица платежей
    await db.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            status TEXT,
            method TEXT,
            txid TEXT,
            date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    await db.execute("CREATE INDEX IF NOT EXISTS idx_pay_user ON payments(user_id);")

    # Таблица сообщений
    await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_text TEXT,
            ai_text TEXT,
            date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    await db.execute("CREATE INDEX IF NOT EXISTS idx_msg_user ON messages(user_id);")

    await db.commit()


# =====================================================
# ФУНКЦИИ (используют единое соединение)
# =====================================================

async def add_user(user_id: int, username: str, referred_by: int = None):
    await db.execute("""
        INSERT OR IGNORE INTO users (user_id, username, referred_by)
        VALUES (?, ?, ?)
    """, (user_id, username, referred_by))
    await db.commit()


async def set_premium(user_id: int, status: bool):
    await db.execute("""
        UPDATE users SET is_premium = ? WHERE user_id = ?
    """, (1 if status else 0, user_id))
    await db.commit()


async def add_balance(user_id: int, amount: float):
    await db.execute("""
        UPDATE users SET balance = balance + ? WHERE user_id = ?
    """, (amount, user_id))
    await db.commit()


# =====================================================
# ПЛАТЁЖИ
# =====================================================

async def log_payment(user_id: int, amount: float, status: str, method: str, txid: str = None):
    await db.execute("""
        INSERT INTO payments (user_id, amount, status, method, txid)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, amount, status, method, txid))
    await db.commit()


# =====================================================
# ЛОГИ СООБЩЕНИЙ
# =====================================================

async def log_message(user_id: int, user_text: str, ai_text: str):
    await db.execute("""
        INSERT INTO messages (user_id, user_text, ai_text)
        VALUES (?, ?, ?)
    """, (user_id, user_text, ai_text))
    await db.commit()


# =====================================================
# КОРРЕКТНОЕ ЗАКРЫТИЕ БД
# =====================================================
async def close_db():
    await db.close()