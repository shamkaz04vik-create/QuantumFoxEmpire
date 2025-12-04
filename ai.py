# ai.py — OpenRouter client (async, aiohttp)
import os
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE = "https://openrouter.ai"
CHAT_ENDPOINT = "/api/v1/chat/completions"
FULL_URL = OPENROUTER_BASE + CHAT_ENDPOINT
DEFAULT_MODEL = "openrouter/gpt-4o-mini"  # можно поменять на желаемую модель

if not OPENROUTER_API_KEY:
    # безопасная падение: не бросаем исключение сразу — вызывающий код проверит и уведомит
    pass

async def ask_openrouter(
    prompt: str,
    system: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 800
) -> Dict[str, Any]:
    """
    Отправляет запрос к OpenRouter Chat Completions и возвращает JSON-ответ.
    Возвращаемый объект: {'success': True, 'text': '...'} или {'success': False, 'error': '...'}
    """
    if not OPENROUTER_API_KEY:
        return {"success": False, "error": "OPENROUTER_API_KEY is not set in environment."}

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    messages: List[Dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            async with session.post(FULL_URL, headers=headers, json=body) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    return {"success": False, "error": f"HTTP {resp.status}: {text}"}
                data = await resp.json()
                # OpenRouter returns structure similar to OpenAI. Разбираем наиболее вероятный ответ:
                # обычно: data['choices'][0]['message']['content'] or data['choices'][0]['text']
                try:
                    choice = data.get("choices", [])[0]
                    # chat-style
                    if choice and "message" in choice and "content" in choice["message"]:
                        out = choice["message"]["content"]
                    elif choice and "text" in choice:
                        out = choice["text"]
                    else:
                        # fallback: try top-level 'result' fields
                        out = str(data)
                except Exception:
                    out = str(data)
                return {"success": True, "text": out, "meta": data}
    except Exception as e:
        return {"success": False, "error": str(e)}
