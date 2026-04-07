from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import BrandProfile, Campaign
from app.schemas import CampaignCreate, CampaignOut, CampaignValidateOut
from app.services.content_generation import validate_campaign_platforms

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


def _brand_dict(b: BrandProfile) -> dict:
    return {
        "brand_name": b.brand_name,
        "industry": b.industry,
        "audience_age": b.audience_age,
        "audience_interests": b.audience_interests,
        "audience_pain_points": b.audience_pain_points,
        "brand_tones": b.brand_tones or [],
        "keywords_include": b.keywords_include,
        "keywords_avoid": b.keywords_avoid,
    }


def _campaign_dict(c: Campaign) -> dict:
    return {
        "name": c.name,
        "goal": c.goal,
        "platforms": c.platforms or [],
        "start_date": c.start_date,
        "end_date": c.end_date,
    }


@router.post("", response_model=CampaignValidateOut)
async def create_campaign(body: CampaignCreate, db: AsyncSession = Depends(get_db)):
    br = await db.execute(select(BrandProfile).where(BrandProfile.id == body.brand_id))
    brand = br.scalar_one_or_none()
    if not brand:
        raise HTTPException(404, "Brand not found")
    c = Campaign(
        brand_id=body.brand_id,
        name=body.name,
        goal=body.goal,
        start_date=body.start_date,
        end_date=body.end_date,
        platforms=body.platforms,
    )
    db.add(c)
    await db.commit()
    await db.refresh(c)
    val = await validate_campaign_platforms(_brand_dict(brand), _campaign_dict(c))
    notes = val.get("notes", "") + "\n" + "\n".join(val.get("warnings", []))
    c.validation_notes = notes.strip()
    await db.commit()
    await db.refresh(c)
    suggestions = list(val.get("suggestions", []))
    return CampaignValidateOut(campaign=c, validation_notes=c.validation_notes or "", suggestions=suggestions)


@router.get("", response_model=list[CampaignOut])
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Campaign).order_by(Campaign.created_at.desc()))
    return list(r.scalars().all())


@router.get("/{campaign_id}", response_model=CampaignOut)
async def get_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    c = r.scalar_one_or_none()
    if not c:
        raise HTTPException(404, "Campaign not found")
    return c
