# db.py
import aiosqlite
import time
from config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            referrer INTEGER,
            balance REAL DEFAULT 0,
            vip_until INTEGER DEFAULT 0,
            joined_at INTEGER DEFAULT (strftime('%s','now'))
        );

        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            url_template TEXT,
            partner_share REAL DEFAULT 0.30,
            user_share REAL DEFAULT 0.20,
            created_at INTEGER DEFAULT (strftime('%s','now'))
        );

        CREATE TABLE IF NOT EXISTS partner_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER,
            user_id INTEGER,
            created_at INTEGER DEFAULT (strftime('%s','now'))
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            partner_id INTEGER,
            amount REAL,
            user_cashback REAL,
            platform_fee REAL,
            status TEXT DEFAULT 'pending',
            note TEXT,
            created_at INTEGER DEFAULT (strftime('%s','now'))
        );

        CREATE TABLE IF NOT EXISTS payout_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            method TEXT,
            details TEXT,
            status TEXT DEFAULT 'pending',
            created_at INTEGER DEFAULT (strftime('%s','now'))
        );
        """)
        await db.commit()

# user helpers
async def add_user_if_not_exists(user_id, username, first_name, referrer=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name, referrer)
            VALUES (?, ?, ?, ?)
        """, (user_id, username or "", first_name or "", referrer))
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id, username, first_name, referrer, balance, vip_until FROM users WHERE user_id = ?", (user_id,))
        return await cur.fetchone()

async def set_referrer(user_id, referrer_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET referrer = ? WHERE user_id = ?", (referrer_id, user_id))
        await db.commit()

async def add_balance(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()

async def set_vip(user_id, until_ts):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET vip_until = ? WHERE user_id = ?", (until_ts, user_id))
        await db.commit()

# partners
async def ensure_default_partners():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM partners")
        cnt = (await cur.fetchone())[0]
        if cnt == 0:
            await db.execute("INSERT INTO partners (name, url_template, partner_share, user_share) VALUES (?, ?, ?, ?)",
                             ("Molniya VPN", "https://t.me/molniya_vpn_bot?start=john0_8_{user}", 0.40, 0.20))
            await db.execute("INSERT INTO partners (name, url_template, partner_share, user_share) VALUES (?, ?, ?, ?)",
                             ("Kovalenko VPN", "https://t.me/Kovalenkovpn_bot?start=john0_8_{user}", 0.35, 0.20))
            await db.commit()

async def list_partners():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, name, url_template, partner_share, user_share FROM partners ORDER BY id")
        return await cur.fetchall()

async def record_partner_click(partner_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO partner_clicks (partner_id, user_id) VALUES (?, ?)", (partner_id, user_id))
        await db.commit()

# transactions
async def record_confirmed_purchase(user_id, partner_id, amount, note=""):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT partner_share, user_share FROM partners WHERE id = ?", (partner_id,))
        p = await cur.fetchone()
        if not p:
            raise ValueError("partner not found")
        partner_share, user_share = p[0], p[1]
        user_cashback = round(amount * user_share, 2)
        partner_commission = round(amount * partner_share, 2)
        platform_fee = round(partner_commission - user_cashback, 2)
        await db.execute("""INSERT INTO transactions (user_id, partner_id, amount, user_cashback, platform_fee, status, note)
                            VALUES (?, ?, ?, ?, ?, 'confirmed', ?)""", (user_id, partner_id, amount, user_cashback, platform_fee, note))
        await db.execute("UPDATE users SET balance = balance + ?, WHERE user_id = ?", (user_cashback, user_id))
        await db.commit()
        return {"user_cashback": user_cashback, "platform_fee": platform_fee}

# stats
async def total_users():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        res = await cur.fetchone()
        return res[0] if res else 0