import csv
import io
from datetime import date, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Campaign, ContentPiece
from app.schemas import CalendarMoveIn
from app.services.calendar_ai import suggest_schedule

router = APIRouter(prefix="/calendar", tags=["calendar"])


class MoveResponse(BaseModel):
    ok: bool


class GapResponse(BaseModel):
    alerts: list[str]


class ScheduleAssignment(BaseModel):
    content_piece_id: str
    scheduled_date: str
    reason: str


class SuggestResponse(BaseModel):
    assignments: list[ScheduleAssignment]


@router.post("/move", response_model=MoveResponse)
async def move_piece(body: CalendarMoveIn, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(ContentPiece).where(ContentPiece.id == body.content_piece_id))
    p = r.scalar_one_or_none()
    if not p:
        raise HTTPException(404, "Content piece not found")
    if body.scheduled_date is None:
        p.scheduled_date = None
        p.status = "Draft"
    else:
        p.scheduled_date = body.scheduled_date
        p.status = "Scheduled"
    await db.commit()
    return {"ok": True}


@router.get("/gaps/{campaign_id}", response_model=GapResponse)
async def gaps(campaign_id: str, db: AsyncSession = Depends(get_db)):
    cr = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    c = cr.scalar_one_or_none()
    if not c:
        raise HTTPException(404, "Campaign not found")
    pr = await db.execute(select(ContentPiece).where(ContentPiece.campaign_id == campaign_id))
    pieces = pr.scalars().all()
    platforms = c.platforms or ["LinkedIn", "Instagram", "Email", "Twitter/X"]
    # Simple week buckets from campaign dates or next 4 weeks
    start = c.start_date or date.today()
    end = c.end_date or (start + timedelta(days=28))
    messages = []
    for w in range(4):
        week_start = start + timedelta(days=7 * w)
        if week_start > end:
            break
        for plat in platforms:
            has = any(
                x.platform == plat and x.scheduled_date and x.scheduled_date >= week_start and x.scheduled_date < week_start + timedelta(days=7)
                for x in pieces
            )
            if not has:
                messages.append(f"You have nothing scheduled for week starting {week_start.isoformat()} on {plat}")
    return {"alerts": messages[:20]}


@router.post("/suggest/{campaign_id}", response_model=SuggestResponse)
async def suggest(campaign_id: str, db: AsyncSession = Depends(get_db)):
    cr = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    c = cr.scalar_one_or_none()
    if not c:
        raise HTTPException(404, "Campaign not found")
    pr = await db.execute(select(ContentPiece).where(ContentPiece.campaign_id == campaign_id))
    pieces = pr.scalars().all()
    piece_info = [{"content_piece_id": p.id, "platform": p.platform, "format_key": p.format_key, "title": p.title} for p in pieces]
    plan = await suggest_schedule(c.platforms or [], c.start_date, c.end_date, piece_info)
    # Fetch all pieces at once instead of N+1 queries
    piece_ids = [a.get("content_piece_id") for a in plan.get("assignments") or []]
    if piece_ids:
        r = await db.execute(select(ContentPiece).where(ContentPiece.id.in_(piece_ids)))
        pieces_by_id = {p.id: p for p in r.scalars().all()}
    else:
        pieces_by_id = {}
    
    for a in plan.get("assignments") or []:
        pid = a.get("content_piece_id")
        sd = a.get("scheduled_date")
        if not pid or not sd or pid not in pieces_by_id:
            continue
        try:
            d = date.fromisoformat(sd[:10])
        except ValueError:
            continue
        cp = pieces_by_id[pid]
        cp.scheduled_date = d
        cp.status = "Scheduled"
    await db.commit()
    return plan


@router.get("/export")
async def export_cal(
    campaign_id: str = Query(...),
    format: str = Query("csv"),
    db: AsyncSession = Depends(get_db),
):
    pr = await db.execute(
        select(ContentPiece).where(ContentPiece.campaign_id == campaign_id).order_by(ContentPiece.scheduled_date.asc())
    )
    pieces = pr.scalars().all()
    if format == "csv":
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["scheduled_date", "platform", "format_key", "status", "title", "body"])
        for p in pieces:
            w.writerow(
                [
                    str(p.scheduled_date) if p.scheduled_date else "",
                    p.platform,
                    p.format_key,
                    p.status,
                    p.title,
                    (p.body or "")[:2000],
                ]
            )
        return PlainTextResponse(buf.getvalue(), media_type="text/csv")
    # PDF as printable HTML
    rows = "".join(
        f"<tr><td>{p.scheduled_date or ''}</td><td>{p.platform}</td><td>{p.status}</td><td>{p.title}</td></tr>"
        for p in pieces
    )
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Calendar</title>
    <style>body{{font-family:system-ui}} table{{border-collapse:collapse;width:100%}} td,th{{border:1px solid #ccc;padding:8px}}</style>
    </head><body><h1>Campaign calendar</h1><table><thead><tr><th>Date</th><th>Platform</th><th>Status</th><th>Title</th></tr></thead><tbody>{rows}</tbody></table></body></html>"""
    return HTMLResponse(html)
