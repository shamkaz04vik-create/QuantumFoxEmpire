import aiosqlite

DB_PATH = "/tmp/database.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT
            )
        """)
        await db.commit()