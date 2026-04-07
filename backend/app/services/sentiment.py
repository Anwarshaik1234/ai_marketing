import csv
import io
import re
from collections import Counter
from typing import Any

from app.services.llm import complete_json


def _word_freq(texts: list[str], stopwords: set[str]) -> list[dict[str, Any]]:
    words: list[str] = []
    for t in texts:
        for w in re.findall(r"[a-zA-Z]{3,}", t.lower()):
            if w not in stopwords:
                words.append(w)
    ctr = Counter(words)
    return [{"text": w, "value": c} for w, c in ctr.most_common(60)]


async def analyze_csv_texts(rows: list[str]) -> dict[str, Any]:
    blob = "\n---\n".join(rows[:500])
    system = (
        "You analyze customer feedback. JSON only:\n"
        '{"positive_pct": 0-100, "neutral_pct": 0-100, "negative_pct": 0-100, '
        '"trend": "up|down|flat", '
        '"positive_themes": [{"theme":"","example":""}, ... max 5], '
        '"negative_themes": [{"theme":"","example":""}, ... max 5], '
        '"emotional_highlights": ["", "", ""], '
        '"voc_paragraph": "", '
        '"campaign_angles": ["", "", ""]}'
    )
    user = f"Comments/reviews:\n{blob[:24000]}"
    llm = await complete_json(system, user, temperature=0.25)
    stops = {
        "the",
        "and",
        "for",
        "that",
        "this",
        "with",
        "you",
        "are",
        "was",
        "but",
        "not",
        "they",
        "have",
        "has",
        "from",
        "our",
        "your",
    }
    llm["wordcloud"] = _word_freq(rows, stops)
    return llm


def parse_csv_column(file_bytes: bytes, text_column: str) -> list[str]:
    text = file_bytes.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return []
    col = text_column if text_column in reader.fieldnames else reader.fieldnames[0]
    out = []
    for row in reader:
        v = (row.get(col) or "").strip()
        if v:
            out.append(v)
    return out
