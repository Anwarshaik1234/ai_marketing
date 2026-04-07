import json
from typing import Any

from app.services.brand_context import build_brand_system_prefix
from app.services.llm import complete_json, complete_text


async def competitor_counter(competitor_post: str, our_brand: dict, campaign: dict | None) -> dict[str, Any]:
    system = (
        build_brand_system_prefix(our_brand, campaign or {})
        + "\nYou suggest how to counter a competitor's message while staying ethical and factual. "
        'JSON: {"summary_competitor_angle": "", "counter_positioning": "", "suggested_post": "", "risks_to_avoid": ""}'
    )
    user = f"Competitor post:\n{competitor_post[:8000]}"
    return await complete_json(system, user, temperature=0.6)


async def tone_score(sample_text: str, brand: dict) -> dict[str, Any]:
    system = (
        "Rate marketing copy against stated brand tones. JSON only: "
        '{"score": 0-100, "rationale": "", "mismatches": [""]}'
    )
    user = json.dumps(
        {
            "brand_tones": brand.get("brand_tones"),
            "keywords_include": brand.get("keywords_include"),
            "keywords_avoid": brand.get("keywords_avoid"),
            "text": sample_text[:6000],
        },
        ensure_ascii=False,
    )
    return await complete_json(system, user, temperature=0.2)
