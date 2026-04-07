import json
from typing import Any

from app.services.llm import complete_json


async def generate_ad_variants(product: str, audience: str, platform: str, goal: str) -> dict[str, Any]:
    system = (
        "You write high-converting ad copy. Return JSON only:\n"
        '{"variants": ['
        '{"id": "v1", "headline": "", "body": "", "tone_label": "Emotional|Logical|Urgency|Social Proof|Curiosity", "cta": ""}'
        " ... exactly 5 items with unique tone_labels covering 5 different tones where possible ]"
        ', "recommended_id": "v?", "recommendation_reason": "one sentence", '
        '"platform_prediction": "one sentence comparing variants for this platform"}'
    )
    user = json.dumps(
        {"product": product, "audience": audience, "platform": platform, "goal": goal},
        ensure_ascii=False,
    )
    data = await complete_json(system, user, temperature=0.8)
    for i, v in enumerate(data.get("variants") or []):
        if isinstance(v, dict):
            v.setdefault("id", f"v{i+1}")
    return data
