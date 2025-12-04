# db.py
import aiosqlite
from config import DB_PATH
import time

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    joined_at INTEGER,
    referrer_id INTEGER DEFAULT NULL,
    balance REAL DEFAULT 0,
    vip_until INTEGER DEFAULT 0
);
"""

CREATE_EVENTS = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_type TEXT,
    payload TEXT,
    created_at INTEGER
);
"""

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_USERS)
        await db.execute(CREATE_EVENTS)
        await db.commit()

async def add_or_update_user(user):
    ts = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users(id, username, first_name, joined_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              username=excluded.username,
              first_name=excluded.first_name
        """, (user.id, user.username or "", user.first_name or "", ts))
        await db.commit()

async def set_referrer(user_id: int, ref_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET referrer_id = ? WHERE id = ?", (ref_id, user_id))
        await db.commit()

async def add_event(user_id, event_type, payload=""):
    ts = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO events(user_id, event_type, payload, created_at) VALUES (?, ?, ?, ?)",
                         (user_id, event_type, payload, ts))
        await db.commit()

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        users = (await cur.fetchone())[0]
        cur = await db.execute("SELECT COUNT(*) FROM events")
        events = (await cur.fetchone())[0]
        return {"users": users, "events": events}

async def add_balance(user_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))
        await db.commit()

async def set_vip(user_id: int, until_ts: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET vip_until = ? WHERE id = ?", (until_ts, user_id))
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, username, first_name, joined_at, referrer_id, balance, vip_until FROM users WHERE id = ?", (user_id,))
        row = await cur.fetchone()
        return row