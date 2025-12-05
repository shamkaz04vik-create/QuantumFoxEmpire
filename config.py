# =====================================================
# ⚙ QuantumFoxEmpire — CONFIG
# =====================================================

import os

# --- BOT ---
BOT_TOKEN = "8456865406:AAGqqDLt4PpMf5QrDEPr7dDXymtTb_eN1_o"
ADMIN_ID = 7209803923

# --- AI: OpenRouter ---
OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "openai/gpt-4o-mini"

# --- Deployment ---
WEBHOOK_URL = "https://quantumfoxempire.onrender.com/webhook"

# --- Database ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # путь к корню проекта
DB_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "database.sqlite3")

# --- Payments ---
CRYPTOBOT_TOKEN = ""
MANUAL_WALLET = "TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# --- VPN Partners ---
VPN_PARTNERS = {
    "molniya": "https://t.me/molniya_vpn_bot?start=john0_8_{user}",
    "kovalenko": "https://t.me/Kovalenkovpn_bot?start=john0_8_{user}"
}