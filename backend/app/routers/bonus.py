from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import BrandProfile, Campaign
from app.services.bonus import competitor_counter, tone_score

router = APIRouter(prefix="/bonus", tags=["bonus"])


class CompetitorIn(BaseModel):
    competitor_post: str
    brand_id: str
    campaign_id: str | None = None


class ToneIn(BaseModel):
    text: str
    brand_id: str


class CompetitorOut(BaseModel):
    summary_competitor_angle: str
    counter_positioning: str
    suggested_post: str
    risks_to_avoid: str


class ToneScoreOut(BaseModel):
    score: int
    rationale: str
    mismatches: list[str]


@router.post("/competitor", response_model=CompetitorOut)
async def competitor(body: CompetitorIn, db: AsyncSession = Depends(get_db)):
    br = await db.execute(select(BrandProfile).where(BrandProfile.id == body.brand_id))
    brand = br.scalar_one_or_none()
    if not brand:
        raise HTTPException(404, "Brand not found")
    camp = None
    if body.campaign_id:
        cr = await db.execute(select(Campaign).where(Campaign.id == body.campaign_id))
        camp = cr.scalar_one_or_none()
    bdict = {
        "brand_name": brand.brand_name,
        "industry": brand.industry,
        "audience_age": brand.audience_age,
        "audience_interests": brand.audience_interests,
        "audience_pain_points": brand.audience_pain_points,
        "brand_tones": brand.brand_tones or [],
        "keywords_include": brand.keywords_include,
        "keywords_avoid": brand.keywords_avoid,
    }
    cdict = None
    if camp:
        cdict = {"name": camp.name, "goal": camp.goal, "platforms": camp.platforms or []}
    return await competitor_counter(body.competitor_post, bdict, cdict)


@router.post("/tone-score", response_model=ToneScoreOut)
async def tone(body: ToneIn, db: AsyncSession = Depends(get_db)):
    br = await db.execute(select(BrandProfile).where(BrandProfile.id == body.brand_id))
    brand = br.scalar_one_or_none()
    if not brand:
        raise HTTPException(404, "Brand not found")
    bdict = {
        "brand_tones": brand.brand_tones or [],
        "keywords_include": brand.keywords_include,
        "keywords_avoid": brand.keywords_avoid,
    }
    return await tone_score(body.text, bdict)
