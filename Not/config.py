# config.py
BOT_TOKEN = "8456865406:AAGqqDLt4PpMf5QrDEPr7dDXymtTb_eN1_o"

# OpenRouter (AI) — твой ключ, вставлен
OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "openai/gpt-4o-mini"

# Админы — добавь сюда свои tg id (числа)
ADMIN_IDS = [7209803923]  # <- замени/добавь свои id если нужно

# Путь к базе (локально в контейнере)
DB_PATH = "data.sqlite"

# VPN партнерки (уже передал тобой)
VPN_PARTNERS = {
    "molniya": "https://t.me/molniya_vpn_bot?start=john0_8_{uid}",
    "kovalenko": "https://t.me/Kovalenkovpn_bot?start=john0_8_{uid}",
}