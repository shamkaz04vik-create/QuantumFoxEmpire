import aiohttp
import asyncio
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL

URL = "https://openrouter.ai/api/v1/chat/completions"

async def ai_answer(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/yourrepo",
        "X-Title": "QuantumFoxEmpireBot",
        "User-Agent": "QuantumFoxEmpireBot"
    }

    body = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(URL, headers=headers, json=body, timeout=30) as resp:

                if resp.status != 200:
                    text = await resp.text()
                    return f"Ошибка API OpenRouter ({resp.status}): {text}"

                data = await resp.json()

                if "choices" not in data:
                    return f"Некорректный ответ AI: {data}"

                return data["choices"][0]["message"]["content"]

    except asyncio.TimeoutError:
        return "AI не отвечает (таймаут). Попробуй ещё раз."
    except Exception as e:
        return f"Ошибка ИИ: {e}"