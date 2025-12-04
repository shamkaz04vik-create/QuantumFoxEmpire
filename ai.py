# ai.py — OpenRouter client (async)
import os
import aiohttp
import json
from typing import Optional, Dict, Any

# ======= ВСТАВЛЕН ТВОЙ КЛЮЧ (по просьбе пользователя) =======
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE = "https://openrouter.ai"
CHAT_ENDPOINT = "/api/v1/chat/completions"
FULL_URL = OPENROUTER_BASE + CHAT_ENDPOINT
DEFAULT_MODEL = "openai/gpt-4o-mini"

async def ask_openrouter(prompt: str,
                        system: Optional[str] = "You are a helpful assistant.",
                        model: str = DEFAULT_MODEL,
                        temperature: float = 0.7,
                        max_tokens: int = 800) -> Dict[str, Any]:
    if not OPENROUTER_API_KEY:
        return {"success": False, "error": "OPENROUTER_API_KEY not set"}

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = []
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
                text = await resp.text()
                if resp.status != 200:
                    return {"success": False, "error": f"HTTP {resp.status}: {text}"}
                data = await resp.json()
                # parse typical OpenRouter/OpenAI-like chat response
                try:
                    choice = data.get("choices", [])[0]
                    if choice and "message" in choice and "content" in choice["message"]:
                        out = choice["message"]["content"]
                    elif choice and "text" in choice:
                        out = choice["text"]
                    else:
                        out = json.dumps(data, ensure_ascii=False)
                except Exception:
                    out = json.dumps(data, ensure_ascii=False)
                return {"success": True, "text": out, "meta": data}
    except Exception as e:
        return {"success": False, "error": str(e)}