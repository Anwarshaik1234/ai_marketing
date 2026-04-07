import csv
import io
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import AdExperiment
from app.schemas import AdLabIn, AdVariantPatch
from app.services.ads import generate_ad_variants

router = APIRouter(prefix="/ads", tags=["ads"])


class AdGenerateOut(BaseModel):
    experiment_id: str
    variants: list[dict[str, Any]]
    recommendation_reason: str
    platform_prediction: str


@router.post("/generate", response_model=AdGenerateOut)
async def gen(body: AdLabIn, db: AsyncSession = Depends(get_db)):
    data = await generate_ad_variants(body.product, body.audience, body.platform, body.goal)
    variants = data.get("variants") or []
    for v in variants:
        v.setdefault("status", "Testing")
    data["variants"] = variants
    exp = AdExperiment(
        product=body.product,
        audience=body.audience,
        platform=body.platform,
        goal=body.goal,
        variants=variants,
        ai_recommendation=(data.get("recommendation_reason") or "") + " | " + (data.get("platform_prediction") or ""),
    )
    db.add(exp)
    await db.commit()
    await db.refresh(exp)
    return {"experiment_id": exp.id, **data}


@router.patch("/experiment/{exp_id}/variant")
async def patch_variant(exp_id: str, body: AdVariantPatch, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(AdExperiment).where(AdExperiment.id == exp_id))
    exp = r.scalar_one_or_none()
    if not exp:
        raise HTTPException(404, "Experiment not found")
    variants: list[dict[str, Any]] = list(exp.variants or [])
    found = False
    for v in variants:
        if v.get("id") == body.variant_id:
            v["status"] = body.status
            found = True
            break
    if not found:
        raise HTTPException(404, f"Variant {body.variant_id} not found")
    exp.variants = variants
    await db.commit()
    return {"ok": True, "variants": variants}


@router.get("/experiment/{exp_id}")
async def get_exp(exp_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(AdExperiment).where(AdExperiment.id == exp_id))
    exp = r.scalar_one_or_none()
    if not exp:
        raise HTTPException(404, "Not found")
    return {
        "id": exp.id,
        "product": exp.product,
        "audience": exp.audience,
        "platform": exp.platform,
        "goal": exp.goal,
        "variants": exp.variants,
        "ai_recommendation": exp.ai_recommendation,
    }


@router.get("/experiment/{exp_id}/export.csv")
async def export_csv(exp_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(AdExperiment).where(AdExperiment.id == exp_id))
    exp = r.scalar_one_or_none()
    if not exp:
        raise HTTPException(404, "Not found")
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "headline", "body", "tone_label", "cta", "status"])
    for v in exp.variants or []:
        w.writerow(
            [
                v.get("id"),
                v.get("headline"),
                v.get("body"),
                v.get("tone_label"),
                v.get("cta"),
                v.get("status", "Testing"),
            ]
        )
    return PlainTextResponse(buf.getvalue(), media_type="text/csv")
