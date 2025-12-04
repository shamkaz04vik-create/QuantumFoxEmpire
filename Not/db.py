import aiosqlite
from config import DB_PATH

# =====================================================
# ИНИЦИАЛИЗАЦИЯ БАЗЫ
# =====================================================
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:

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

        # Логи сообщений для ИИ
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


# =====================================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ
# =====================================================

async def add_user(user_id: int, username: str, referred_by: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, referred_by)
            VALUES (?, ?, ?)
        """, (user_id, username, referred_by))
        await db.commit()


async def set_premium(user_id: int, status: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET is_premium = ? WHERE user_id = ?
        """, (1 if status else 0, user_id))
        await db.commit()


async def add_balance(user_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET balance = balance + ? WHERE user_id = ?
        """, (amount, user_id))
        await db.commit()


# =====================================================
# ПЛАТЕЖИ
# =====================================================

async def log_payment(user_id: int, amount: float, status: str, method: str, txid: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO payments (user_id, amount, status, method, txid)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, amount, status, method, txid))
        await db.commit()


# =====================================================
# ЛОГИ ДИАЛОГОВ
# =====================================================

async def log_message(user_id: int, user_text: str, ai_text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO messages (user_id, user_text, ai_text)
            VALUES (?, ?, ?)
        """, (user_id, user_text, ai_text))
        await db.commit()