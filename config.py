# config.py — полный конфиг
BOT_TOKEN = "8456865406:AAGqqDLt4PpMf5QrDEPr7dDXymtTb_eN1_o"
ADMIN_ID = 7209803923

# OpenRouter (твой ключ)
OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "openai/gpt-4o-mini"

# Deployment URL (Render)
WEBHOOK_URL = "https://quantumfoxempire.onrender.com/webhook"  # убедись, что совпадает с настройкой на Render

# Database path — локальный файл в рабочей директории (Render writable)
DB_PATH = "./data/database.db"   # относительный путь — проще управлять правами

# Payments
CRYPTOBOT_TOKEN = ""
MANUAL_WALLET = "TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# VPN partners
VPN_PARTNERS = {
    "molniya": "https://t.me/molniya_vpn_bot?start=john0_8_{user}",
    "kovalenko": "https://t.me/Kovalenkovpn_bot?start=john0_8_{user}"
}