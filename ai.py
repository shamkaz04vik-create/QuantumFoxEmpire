import aiohttp

API_KEY = "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"

URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"


async def ai_answer(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(URL, headers=headers, json=body) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Ошибка ИИ: {e}"