import aiohttp
import json

API_KEY = "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"
URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"


async def ai_answer(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/yourbot",  
        "X-Title": "KazbekRecruitBot"
    }

    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Ты умный помощник телеграм-бота для подборки работников."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(URL, headers=headers, json=body) as resp:

                if resp.status != 200:
                    text = await resp.text()
                    return f"Ошибка от OpenRouter ({resp.status}): {text}"

                data = await resp.json()

                # OpenRouter структура:
                # data["choices"][0]["message"]["content"]
                choice = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )

                if not choice:
                    return f"Ошибка: пустой ответ ИИ. Полные данные:\n{json.dumps(data, ensure_ascii=False, indent=2)}"

                return choice

    except Exception as e:
        return f"Ошибка ИИ: {e}"