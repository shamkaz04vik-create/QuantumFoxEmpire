# payments.py
import aiohttp
import time
from config import CRYPTOBOT_TOKEN, MANUAL_WALLET
from db import add_balance, set_vip, add_user_if_not_exists

# If CRYPTOBOT_TOKEN provided, try to create invoice via that API.
# If not provided, we fallback to manual instructions: user transfers to MANUAL_WALLET and sends proof,
# admin uses /confirm_payment to credit user.

async def create_crypto_invoice(user_id: int, amount_usd: float):
    if not CRYPTOBOT_TOKEN:
        return None
    url = "https://pay.crypt.bot/api/createInvoice"  # fictional: adjust if real API exists
    headers = {"Authorization": f"Bearer {CRYPTOBOT_TOKEN}"}
    payload = {"amount": amount_usd, "currency": "USDT"}
    async with aiohttp.ClientSession() as s:
        async with s.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data.get("pay_url")

async def manual_payment_instructions():
    # returns wallet & instructions
    return {
        "wallet": MANUAL_WALLET,
        "instructions": f"Переведите нужную сумму в USDT (TRC20) на адрес {MANUAL_WALLET}. "
                        "После перевода отправьте скриншот/txid через кнопку 'Сообщить оплату' — админ проверит и подтвердит."
    }

# admin confirms a manual payment
async def confirm_manual_payment(user_id: int, amount: float, admin_id: int, db_module=None):
    # give balance or VIP - example: if amount >= threshold, give VIP 30 days
    ts = int(time.time())
    if amount >= 7:  # example price for VIP month (in USD)
        until = ts + 30*24*3600
        await set_vip(user_id, until)
        # log in DB via add_balance or events (handled elsewhere)
        return {"ok": True, "type": "vip", "until": until}
    else:
        await add_balance(user_id, amount)
        return {"ok": True, "type": "balance", "amount": amount}