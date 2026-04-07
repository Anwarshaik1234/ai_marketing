import hashlib
import re
from typing import Any

from app.services.brand_context import build_brand_system_prefix
from app.services.llm import complete_json


def _split_sections(text: str) -> list[dict[str, Any]]:
    """Rough sections for coverage map (paragraph-based)."""
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    sections = []
    for i, p in enumerate(parts[:40]):
        sections.append({"id": i, "preview": p[:200], "hash": hashlib.sha256(p.encode()).hexdigest()[:12]})
    return sections


async def analyze_source(asset_name: str, text: str) -> dict[str, Any]:
    system = (
        "You extract structure from long-form marketing source text. "
        'JSON only: {"insights": [5 strings], "quotable": [5 strings], "argument_summary": "paragraph"}'
    )
    user = f"Asset: {asset_name}\n\nText:\n{text[:12000]}"
    base = await complete_json(system, user, temperature=0.4)
    sections = _split_sections(text)
    base["sections"] = sections
    return base


def build_coverage_map(generated_snippets: list[str], sections: list[dict]) -> dict[str, Any]:
    """Heuristic: match hashes of section text to which outputs referenced ideas."""
    scores: dict[str, float] = {str(s["id"]): 0.0 for s in sections}
    for snip in generated_snippets:
        low = snip.lower()
        for s in sections:
            prev = (s.get("preview") or "").lower()
            if len(prev) > 20 and prev[:40] in low:
                scores[str(s["id"])] += 1.0
    return {"section_scores": scores, "labels": [s["preview"][:80] for s in sections]}


async def repurposed_bundle(
    brand: dict,
    campaign: dict,
    asset_name: str,
    text: str,
    analysis: dict[str, Any],
) -> dict[str, Any]:
    from app.services.content_generation import GENERATION_SCHEMA_HINT

    system = (
        build_brand_system_prefix(brand, campaign)
        + "\nYou may ONLY use ideas and facts from the provided source. "
        + 'Each text field should end with a short attribution note like: Based on "'
        + asset_name
        + '".\n'
        + GENERATION_SCHEMA_HINT
    )
    user = (
        f'Source asset: "{asset_name}"\n'
        f"Key insights: {analysis.get('insights')}\n"
        f"Argument: {analysis.get('argument_summary')}\n\n"
        f"Source text:\n{text[:14000]}"
    )
    return await complete_json(system, user, temperature=0.65)
