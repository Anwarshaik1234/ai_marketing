from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import BrandProfile
from app.schemas import BrandCreate, BrandOut

router = APIRouter(prefix="/brands", tags=["brands"])


@router.post("", response_model=BrandOut)
async def create_brand(body: BrandCreate, db: AsyncSession = Depends(get_db)):
    tones = (body.brand_tones or [])[:3]
    b = BrandProfile(
        brand_name=body.brand_name,
        industry=body.industry,
        audience_age=body.audience_age,
        audience_interests=body.audience_interests,
        audience_pain_points=body.audience_pain_points,
        brand_tones=tones,
        keywords_include=body.keywords_include,
        keywords_avoid=body.keywords_avoid,
    )
    db.add(b)
    await db.commit()
    await db.refresh(b)
    return b


@router.get("", response_model=list[BrandOut])
async def list_brands(db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(BrandProfile).order_by(BrandProfile.created_at.desc()))
    return list(r.scalars().all())


@router.get("/{brand_id}", response_model=BrandOut)
async def get_brand(brand_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(BrandProfile).where(BrandProfile.id == brand_id))
    b = r.scalar_one()
    return b
