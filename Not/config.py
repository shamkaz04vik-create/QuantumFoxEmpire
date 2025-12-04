# =====================================================
# ⚙ QuantumFoxEmpire — CONFIG
# =====================================================

# --- BOT ---
BOT_TOKEN = "8456865406:AAGqqDLt4PpMf5QrDEPr7dDXymtTb_eN1_o"
ADMIN_ID = 7209803923

# --- AI: OpenRouter ---
OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "openai/gpt-4o-mini"

# --- Deployment ---
WEBHOOK_URL = "https://quantumfoxempire.onrender.com/webhook"

# --- Database (обязательно подключить в db.py) ---
DB_PATH = "/data/database.db"

# --- Payments ---
CRYPTOBOT_TOKEN = ""  # если нет — оставить пустым
MANUAL_WALLET = "TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # USDT TRC20

# --- VPN Partners ---
VPN_PARTNERS = {
    "molniya": "https://t.me/molniya_vpn_bot?start=john0_8_{user}",
    "kovalenko": "https://t.me/Kovalenkovpn_bot?start=john0_8_{user}"
}