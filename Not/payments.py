import aiohttp
from config import CRYPTOBOT_TOKEN
from vip import VIP_PRICES

API_URL = "https://pay.crypt.bot/api/"

async def create_invoice(user_id, level):
    price = VIP_PRICES[level]

    async with aiohttp.ClientSession() as session:
        async with session.post(
            API_URL + "createInvoice",
            headers={"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN},
            json={"amount": price, "currency_type": "crypto", "asset": "USDT"}
        ) as resp:
            data = await resp.json()
            return data["result"]["pay_url"]