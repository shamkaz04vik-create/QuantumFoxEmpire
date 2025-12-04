# config.py
# ВНИМАНИЕ: тут вставлены токены как просил пользователь.
BOT_TOKEN = "8456865406:AAGqqDLt4PpMf5QrDEPr7dDXymtTb_eN1_o"
ADMIN_ID = 7209803923

# OpenRouter (AI)
OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "openai/gpt-4o-mini"

# Webhook (Render)
WEBHOOK_URL = "https://quantumfoxempire.onrender.com/webhook"

# Database
DB_PATH = "/data/database.db"  # рекомендую смонтировать persistent disk /data на Render

# Payments: если у тебя есть CryptoBot token, можно вставить сюда,
# иначе система предложит инструкции для ручной оплаты и админ-подтверждение.
CRYPTOBOT_TOKEN = ""  # <-- если есть - вставь сюда токен от @CryptoBot API

# Wallet for manual payments (USDT TRC20) — замените на свой адрес если есть
MANUAL_WALLET = "TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# VPN partners templates (подставляется {user})
VPN_PARTNERS = {
    "molniya": "https://t.me/molniya_vpn_bot?start=john0_8_{user}",
    "kovalenko": "https://t.me/Kovalenkovpn_bot?start=john0_8_{user}"
}