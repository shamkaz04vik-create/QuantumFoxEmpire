import aiohttp
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL

URL = "https://openrouter.ai/api/v1/chat/completions"

async def ai_answer(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/project",
        "X-Title": "QuantumFoxEmpireBot"
    }

    body = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(URL, headers=headers, json=body) as resp:

            if resp.status != 200:
                return f"Ошибка AI ({resp.status}): {await resp.text()}"

            data = await resp.json()
            return data["choices"][0]["message"]["content"]