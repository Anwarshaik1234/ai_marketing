def build_brand_system_prefix(brand: dict, campaign: dict | None = None) -> str:
    tones = ", ".join(brand.get("brand_tones") or [])
    lines = [
        "You are an expert marketing copywriter.",
        "Every output MUST respect this brand context:",
        f"Brand: {brand.get('brand_name', '')}",
        f"Industry: {brand.get('industry', '')}",
        f"Target audience — age: {brand.get('audience_age', '')}; interests: {brand.get('audience_interests', '')}; pain points: {brand.get('audience_pain_points', '')}",
        f"Brand tone (use consistently, blend naturally): {tones}",
        f"Always try to naturally include these keywords/phrases when relevant: {brand.get('keywords_include', '')}",
        f"Never use these words/phrases: {brand.get('keywords_avoid', '')}",
    ]
    if campaign:
        lines.extend(
            [
                f"Campaign: {campaign.get('name', '')}",
                f"Campaign goal: {campaign.get('goal', '')}",
                f"Platforms in scope: {', '.join(campaign.get('platforms') or [])}",
            ]
        )
    return "\n".join(lines)
