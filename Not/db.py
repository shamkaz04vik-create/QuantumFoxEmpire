# db.py
import os
import asyncpg
from datetime import datetime
from typing import Optional

DATABASE_URL = os.getenv("DATABASE_URL")  # must be set in Render env

async def create_pool():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return pool

async def init_db(pool):
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE,
            username TEXT,
            first_name TEXT,
            referrer_id BIGINT,
            balance NUMERIC DEFAULT 0,
            earned_total NUMERIC DEFAULT 0,
            joined_at TIMESTAMP DEFAULT now()
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS partners (
            id SERIAL PRIMARY KEY,
            name TEXT,
            url_template TEXT,
            category TEXT,
            partner_share NUMERIC DEFAULT 0.30,
            user_share NUMERIC DEFAULT 0.20,
            created_at TIMESTAMP DEFAULT now()
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS partner_clicks (
            id SERIAL PRIMARY KEY,
            partner_id INTEGER REFERENCES partners(id),
            user_id BIGINT,
            created_at TIMESTAMP DEFAULT now()
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            partner_id INTEGER,
            amount NUMERIC,
            user_cashback NUMERIC,
            platform_fee NUMERIC,
            status TEXT DEFAULT 'pending',
            note TEXT,
            created_at TIMESTAMP DEFAULT now()
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS payout_requests (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            amount NUMERIC,
            method TEXT,
            details TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT now()
        );
        """)
        # ensure default partners exist
        row = await conn.fetchrow("SELECT COUNT(*) AS c FROM partners")
        if row and row["c"] == 0:
            await conn.execute("""
                INSERT INTO partners (name, url_template, category, partner_share, user_share)
                VALUES ($1, $2, $3, $4, $5)
            """, "Molniya VPN", "https://t.me/molniya_vpn_bot?start=john0_8_{user}", "vpn", 0.40, 0.20)
            await conn.execute("""
                INSERT INTO partners (name, url_template, category, partner_share, user_share)
                VALUES ($1, $2, $3, $4, $5)
            """, "Kovalenko VPN", "https://t.me/Kovalenkovpn_bot?start=john0_8_{user}", "vpn", 0.35, 0.20)
