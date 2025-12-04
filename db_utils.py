# db_utils.py
import aiosqlite
from datetime import datetime

DB_DEFAULT = "/data/database.db"

async def init_db(db_path=DB_DEFAULT):
    async with aiosqlite.connect(db_path) as db:
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            balance REAL DEFAULT 0,
            earned_total REAL DEFAULT 0,
            referrer INTEGER DEFAULT NULL,
            joined_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            url_template TEXT,
            category TEXT,
            partner_share REAL DEFAULT 0.30,
            user_share REAL DEFAULT 0.20,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS partner_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER,
            user_id INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
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
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS payout_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            method TEXT,
            details TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now'))
        );
        """)
        await db.commit()

async def ensure_default_partners(db_path=DB_DEFAULT):
    # Add your two vpn partners if table empty
    async with aiosqlite.connect(db_path) as db:
        cur = await db.execute("SELECT COUNT(*) FROM partners")
        row = await cur.fetchone()
        count = row[0] if row else 0
        if count == 0:
            partners = [
                ("Molniya VPN", "https://t.me/molniya_vpn_bot?start=john0_8_{user}", "vpn", 0.40, 0.20),
                ("Kovalenko VPN", "https://t.me/Kovalenkovpn_bot?start=john0_8_{user}", "vpn", 0.35, 0.20),
            ]
            for name, url, cat, pshare, ushare in partners:
                await db.execute(
                    "INSERT INTO partners (name, url_template, category, partner_share, user_share, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, url, cat, pshare, ushare, datetime.utcnow().isoformat())
                )
            await db.commit()

# User functions
async def add_user_if_not_exists(user_id, username, first_name, referrer=None, db_path=DB_DEFAULT):
    async with aiosqlite.connect(db_path) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if await cur.fetchone():
            return False
        await db.execute(
            "INSERT INTO users (user_id, username, first_name, referrer, joined_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, username or "", first_name or "", referrer, datetime.utcnow().isoformat())
        )
        # bonuses if referrer
        if referrer:
            await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (20.0, referrer))
            await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (10.0, user_id))
            await db.execute("INSERT INTO transactions (user_id, amount, user_cashback, platform_fee, status, note, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (referrer, 0.0, 20.0, 0.0, 'confirmed', f'ref_bonus_from_{user_id}', datetime.utcnow().isoformat()))
            await db.execute("INSERT INTO transactions (user_id, amount, user_cashback, platform_fee, status, note, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (user_id, 0.0, 10.0, 0.0, 'confirmed', 'welcome_bonus', datetime.utcnow().isoformat()))
        await db.commit()
        return True

async def get_user_stats(user_id, db_path=DB_DEFAULT):
    async with aiosqlite.connect(db_path) as db:
        cur = await db.execute("SELECT balance, earned_total, referrer FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        if not row:
            return None
        balance, earned_total, referrer = row
        cur2 = await db.execute("SELECT COUNT(*) FROM users WHERE referrer = ?", (user_id,))
        refs = (await cur2.fetchone())[0]
        return {"balance": balance, "earned_total": earned_total, "referrer": referrer, "refs": refs}

# Partners / clicks / transactions
async def list_partners(db_path=DB_DEFAULT):
    async with aiosqlite.connect(db_path) as db:
        cur = await db.execute("SELECT id, name, url_template, category, partner_share, user_share FROM partners ORDER BY id")
        return await cur.fetchall()

async def get_partner(db_path, pid):
    async with aiosqlite.connect(db_path) as db:
        cur = await db.execute("SELECT id, name, url_template, partner_share, user_share FROM partners WHERE id = ?", (pid,))
        return await cur.fetchone()

async def record_partner_click(partner_id, user_id, db_path=DB_DEFAULT):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("INSERT INTO partner_clicks (partner_id, user_id, created_at) VALUES (?, ?, ?)",
                         (partner_id, user_id, datetime.utcnow().isoformat()))
        await db.commit()

async def partner_clicks_stats(db_path=DB_DEFAULT):
    async with aiosqlite.connect(db_path) as db:
        cur = await db.execute("""
            SELECT p.id, p.name, p.category, COUNT(pc.id) as clicks
            FROM partners p
            LEFT JOIN partner_clicks pc ON pc.partner_id = p.id
            GROUP BY p.id ORDER BY clicks DESC
        """)
        return await cur.fetchall()

# confirm purchase (admin or partner callback)
async def record_confirmed_purchase(user_id, partner_id, amount, note="", db_path=DB_DEFAULT):
    async with aiosqlite.connect(db_path) as db:
        cur = await db.execute("SELECT partner_share, user_share FROM partners WHERE id = ?", (partner_id,))
        row = await cur.fetchone()
        if not row:
            raise ValueError("partner not found")
        partner_share, user_share = row
        user_cashback = round(amount * user_share, 2)
        partner_commission = round(amount * partner_share, 2)
        platform_fee = round(partner_commission - user_cashback, 2)
        await db.execute("""
            INSERT INTO transactions (user_id, partner_id, amount, user_cashback, platform_fee, status, note, created_at)
            VALUES (?, ?, ?, ?, ?, 'confirmed', ?, ?)""",
            (user_id, partner_id, amount, user_cashback, platform_fee, note, datetime.utcnow().isoformat()))
        await db.execute("UPDATE users SET balance = balance + ?, earned_total = earned_total + ? WHERE user_id = ?",
                         (user_cashback, user_cashback, user_id))
        await db.commit()
        return {"user_cashback": user_cashback, "platform_fee": platform_fee}

# payouts
async def create_payout_request(user_id, amount, method, details, db_path=DB_DEFAULT):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("INSERT INTO payout_requests (user_id, amount, method, details, status, created_at) VALUES (?, ?, ?, ?, 'pending', ?)",
                         (user_id, amount, method, details, datetime.utcnow().isoformat()))
        # reduce user's balance immediately (simple reservation)
        await db.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
        await db.commit()

async def list_payouts(db_path=DB_DEFAULT):
    async with aiosqlite.connect(db_path) as db:
        cur = await db.execute("SELECT id, user_id, amount, method, details, status, created_at FROM payout_requests ORDER BY created_at DESC")
        return await cur.fetchall()

async def set_payout_status(payout_id, status, db_path=DB_DEFAULT):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE payout_requests SET status = ? WHERE id = ?", (status, payout_id))
        await db.commit()