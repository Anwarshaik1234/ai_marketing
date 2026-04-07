import json
from datetime import date, timedelta
from typing import Any

from app.services.llm import complete_json


async def suggest_schedule(
    platforms: list[str],
    start: date | None,
    end: date | None,
    pieces: list[dict[str, Any]],
) -> dict[str, Any]:
    system = (
        "Given content pieces and date range, propose scheduled_date for each id. "
        "Respect platform best practices (e.g. LinkedIn weekday mornings). "
        'JSON: {"assignments": [{"content_piece_id":"","scheduled_date":"YYYY-MM-DD","reason":""}]}'
    )
    user = json.dumps(
        {
            "platforms": platforms,
            "start": str(start) if start else None,
            "end": str(end) if end else None,
            "pieces": pieces,
        },
        ensure_ascii=False,
    )
    return await complete_json(system, user, temperature=0.3)
