from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import SentimentReport
from app.services.sentiment import analyze_csv_texts, parse_csv_column

router = APIRouter(prefix="/sentiment", tags=["sentiment"])


class SentimentAnalysisOut(BaseModel):
    report_id: str
    positive_pct: int
    neutral_pct: int
    negative_pct: int
    trend: str
    positive_themes: list[dict[str, str]]
    negative_themes: list[dict[str, str]]
    emotional_highlights: list[str]
    voc_paragraph: str
    campaign_angles: list[str]
    wordcloud: list[dict[str, Any]]


class SentimentReportItem(BaseModel):
    id: str
    created_at: str
    source: str


@router.post("/upload", response_model=SentimentAnalysisOut)
async def upload(
    file: UploadFile = File(...),
    text_column: str = Form("text"),
    db: AsyncSession = Depends(get_db),
):
    try:
        raw = await file.read()
        rows = parse_csv_column(raw, text_column)
    except Exception as e:
        raise HTTPException(400, f"Failed to read CSV file: {str(e)}")
    
    if not rows:
        raise HTTPException(400, "No rows found — check CSV and column name")
    
    summary = await analyze_csv_texts(rows)
    rep = SentimentReport(source_filename=file.filename or "upload.csv", summary=summary)
    db.add(rep)
    await db.commit()
    await db.refresh(rep)
    return {"report_id": rep.id, **summary}


@router.get("/reports", response_model=list[SentimentReportItem])
async def list_reports(db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(SentimentReport).order_by(SentimentReport.created_at.desc()).limit(30))
    reps = r.scalars().all()
    return [{"id": x.id, "created_at": x.created_at.isoformat(), "source": x.source_filename} for x in reps]


@router.get("/reports/{report_id}", response_model=SentimentAnalysisOut)
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(SentimentReport).where(SentimentReport.id == report_id))
    rep = r.scalar_one_or_none()
    if not rep:
        raise HTTPException(404, "Report not found")
    return {"report_id": rep.id, **rep.summary}
