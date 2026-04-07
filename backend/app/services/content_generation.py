import json
from typing import Any

from app.services.brand_context import build_brand_system_prefix
from app.services.llm import complete_json


GENERATION_SCHEMA_HINT = """
Return a single JSON object with these keys (all strings unless specified):
- linkedin: array of exactly 3 objects: { "style": "thought_leadership"|"story"|"direct_cta", "text": "..." }
- instagram: { "caption": "emoji-friendly caption + line breaks", "hashtags": "#tag1 #tag2", "caption_no_emoji": "same caption without any emojis" }
- twitter: array of exactly 5 objects: { "angle": "stat"|"question"|"hot_take"|"tip"|"announcement", "text": "..." }
- video_30: { "hook": "", "body": "", "cta": "" }
- video_60: { "hook": "", "body": "", "cta": "" }
- email: { "subject": "", "body": "", "cta": "" }
- blog_outline: { "h1": "", "sections": [ { "h2": "", "key_points": [], "suggested_words": 0 } ] }
- google_ads: array of 3 objects: { "headline": "", "description": "" }
- seo: { "meta_title": "", "meta_description": "" }
No markdown fences. Valid JSON only.
"""


async def generate_all_formats(
    brand: dict,
    campaign: dict,
    topic: str,
    brief: str,
) -> dict[str, Any]:
    system = build_brand_system_prefix(brand, campaign) + "\n" + GENERATION_SCHEMA_HINT
    user = f"Topic: {topic}\nAdditional brief: {brief}\nGenerate the full JSON package."
    data = await complete_json(system, user, temperature=0.75)
    return data


async def validate_campaign_platforms(brand: dict, campaign: dict) -> dict[str, Any]:
    system = (
        "You validate marketing campaign setup. Respond with JSON only: "
        '{"notes": "paragraph", "suggestions": ["short tip", ...], "warnings": ["tone vs platform", ...]}'
    )
    user = json.dumps(
        {
            "brand_tones": brand.get("brand_tones"),
            "platforms": campaign.get("platforms"),
            "goal": campaign.get("goal"),
            "industry": brand.get("industry"),
        },
        ensure_ascii=False,
    )
    return await complete_json(system, user, temperature=0.3)
