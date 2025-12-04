import asyncpg
from config import DATABASE_URL

async def db_connect():
    db = await asyncpg.create_pool(DATABASE_URL)
    return db

async def init_db(db):
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            vip_level TEXT DEFAULT 'free',
            referrer BIGINT,
            created TIMESTAMP DEFAULT NOW()
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            amount NUMERIC,
            vip_level TEXT,
            status TEXT,
            timestamp TIMESTAMP DEFAULT NOW()
        );
    """)