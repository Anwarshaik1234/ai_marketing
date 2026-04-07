from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import BrandProfile, Campaign, ContentPiece, RepurposeJob
from app.schemas import RepurposeIn
from app.routers.content import _brand, _camp, _flatten_generated
from app.services.repurpose import analyze_source, build_coverage_map, repurposed_bundle

router = APIRouter(prefix="/repurpose", tags=["repurpose"])


class AnalysisOut(BaseModel):
    insights: list[str]
    quotable: list[str]
    argument_summary: str
    sections: list[dict[str, Any]]


class RepurposeRunOut(BaseModel):
    job_id: str
    analysis: dict[str, Any]
    coverage_map: dict[str, Any]
    generated: dict[str, Any]
    content_piece_ids: list[str]


class JobListItem(BaseModel):
    id: str
    asset_name: str
    asset_type: str
    created_at: str
    has_coverage: bool


class AnalyzeIn(BaseModel):
    asset_name: str
    text: str


@router.post("/analyze", response_model=AnalysisOut)
async def analyze(body: AnalyzeIn):
    analysis = await analyze_source(body.asset_name, body.text)
    return analysis


@router.post("/run", response_model=RepurposeRunOut)
async def run_repurpose(body: RepurposeIn, db: AsyncSession = Depends(get_db)):
    cr = await db.execute(
        select(Campaign, BrandProfile)
        .join(BrandProfile, Campaign.brand_id == BrandProfile.id)
        .where(Campaign.id == body.campaign_id)
    )
    row = cr.first()
    if not row:
        raise HTTPException(404, "Campaign not found")
    campaign, brand = row
    analysis = await analyze_source(body.asset_name, body.text)
    bundle = await repurposed_bundle(_brand(brand), _camp(campaign), body.asset_name, body.text, analysis)
    attr = f'Based on "{body.asset_name}"'
    pieces_models = _flatten_generated(campaign.id, bundle, body.asset_name, attribution=attr)
    snippets = [p.body for p in pieces_models]
    coverage = build_coverage_map(snippets, analysis.get("sections") or [])
    job = RepurposeJob(
        asset_name=body.asset_name,
        asset_type=body.asset_type,
        raw_text=body.text[:50000],
        coverage_map=coverage,
        insights={
            "insights": analysis.get("insights"),
            "quotable": analysis.get("quotable"),
            "argument_summary": analysis.get("argument_summary"),
        },
    )
    db.add(job)
    for p in pieces_models:
        db.add(p)
    await db.commit()
    await db.refresh(job)
    return {"job_id": job.id, "analysis": analysis, "coverage_map": coverage, "generated": bundle, "content_piece_ids": [p.id for p in pieces_models]}


@router.get("/jobs", response_model=list[JobListItem])
async def list_jobs(db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(RepurposeJob).order_by(RepurposeJob.created_at.desc()).limit(50))
    jobs = r.scalars().all()
    return [
        {
            "id": j.id,
            "asset_name": j.asset_name,
            "asset_type": j.asset_type,
            "created_at": j.created_at.isoformat(),
            "has_coverage": bool(j.coverage_map),
        }
        for j in jobs
    ]
