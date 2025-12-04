# ai.py
import aiohttp
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL
import asyncio

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

async def ai_answer(prompt: str, model: str = OPENROUTER_MODEL, max_tokens: int = 700, temperature: float = 0.2) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OPENROUTER_URL, headers=headers, json=body, timeout=60) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    return f"Ошибка OpenRouter ({resp.status}): {text}"
                data = await resp.json()
                # OpenRouter обычно возвращает data['choices'][0]['message']['content']
                try:
                    return data["choices"][0]["message"]["content"]
                except Exception:
                    # fallback: pretty print
                    return str(data)
    except asyncio.TimeoutError:
        return "Ошибка: таймаут запроса к ИИ."
    except Exception as e:
        return f"Ошибка ИИ: {e}"