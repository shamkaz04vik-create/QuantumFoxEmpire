import aiosqlite

DB_NAME = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                referrer INTEGER,
                joined_at TEXT
            )
        """)
        await db.commit()

async def add_user(user_id: int, ref: int | None):
    async with aiosqlite.connect(DB_NAME) as db:
        existing = await db.execute_fetchone(
            "SELECT user_id FROM users WHERE user_id = ?", (user_id,)
        )
        if existing:
            return
        await db.execute(
            "INSERT INTO users (user_id, referrer, joined_at) VALUES (?, ?, datetime('now'))",
            (user_id, ref)
        )
        await db.commit()

async def count_users():
    async with aiosqlite.connect(DB_NAME) as db:
        row = await db.execute_fetchone("SELECT COUNT(*) FROM users")
        return row[0]

async def count_refs(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        row = await db.execute_fetchone("SELECT COUNT(*) FROM users WHERE referrer = ?", (user_id,))
        return row[0]