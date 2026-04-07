import json
import re
from typing import Any, Optional

import httpx
from openai import AsyncOpenAI

from app.config import settings

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def _strip_json_fence(text: str) -> str:
    text = text.strip()
    m = re.match(r"^```(?:json)?\s*([\s\S]*?)```$", text)
    if m:
        return m.group(1).strip()
    return text


async def complete_json(
    system: str,
    user: str,
    *,
    temperature: float = 0.7,
) -> dict[str, Any]:
    """Returns parsed JSON from the model."""
    content = await complete_text(system, user, temperature=temperature)
    raw = _strip_json_fence(content)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Last resort: extract first {...} block
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw[start : end + 1])
        raise


def _resolved_llm_backend() -> str:
    """Returns 'ollama' | 'groq' | 'openai'."""
    if settings.ollama_only:
        return "ollama"
    p = (settings.llm_provider or "auto").strip().lower()
    if p == "ollama":
        return "ollama"
    if p == "groq":
        return "groq" if settings.groq_api_key else "ollama"
    if p == "openai":
        return "openai" if settings.openai_api_key else "ollama"
    # auto
    if settings.openai_api_key:
        return "openai"
    if settings.groq_api_key:
        return "groq"
    return "ollama"


async def _openai_compatible_chat(
    *,
    api_key: str,
    base_url: Optional[str],
    model: str,
    system: str,
    user: str,
    temperature: float,
) -> str:
    kwargs: dict = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = AsyncOpenAI(**kwargs)
    resp = await client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return (resp.choices[0].message.content or "").strip()


async def complete_text(
    system: str,
    user: str,
    *,
    temperature: float = 0.7,
) -> str:
    backend = _resolved_llm_backend()
    if backend == "ollama":
        return await _ollama_chat(system, user, temperature)
    if backend == "groq":
        return await _openai_compatible_chat(
            api_key=settings.groq_api_key,
            base_url=GROQ_BASE_URL,
            model=settings.groq_model,
            system=system,
            user=user,
            temperature=temperature,
        )
    base = (settings.openai_base_url or "").strip() or None
    return await _openai_compatible_chat(
        api_key=settings.openai_api_key,
        base_url=base,
        model=settings.openai_model,
        system=system,
        user=user,
        temperature=temperature,
    )


async def _ollama_chat(system: str, user: str, temperature: float) -> str:
    url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"
    payload = {
        "model": settings.ollama_model,
        "stream": False,
        "options": {"temperature": temperature},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
    return (data.get("message") or {}).get("content") or data.get("response") or ""
