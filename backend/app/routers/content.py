from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import BrandProfile, Campaign, ContentPiece
from app.schemas import ContentGenerateIn, ContentRegenerateIn
from app.services.brand_context import build_brand_system_prefix
from app.services.content_generation import generate_all_formats
from app.services.llm import complete_text

router = APIRouter(prefix="/content", tags=["content"])


def _brand(b: BrandProfile) -> dict:
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


def _camp(c: Campaign) -> dict:
    return {
        "name": c.name,
        "goal": c.goal,
        "platforms": c.platforms or [],
    }


def _flatten_generated(
    campaign_id: str,
    data: dict[str, Any],
    topic: str,
    attribution: str | None = None,
) -> list[ContentPiece]:
    pieces: list[ContentPiece] = []
    attr = attribution

    def add(
        platform: str,
        format_key: str,
        title: str,
        body: str,
        extra: dict | None = None,
    ):
        pieces.append(
            ContentPiece(
                campaign_id=campaign_id,
                platform=platform,
                format_key=format_key,
                title=title,
                body=body,
                extra=extra,
                status="Draft",
                attribution=attr,
            )
        )

    for i, li in enumerate(data.get("linkedin") or []):
        add("LinkedIn", f"linkedin_{i+1}", li.get("style", ""), li.get("text", ""), li)
    ig = data.get("instagram") or {}
    if ig:
        body = f"{ig.get('caption', '')}\n\nHashtags: {ig.get('hashtags', '')}"
        add("Instagram", "instagram", "Main", body, ig)
        if ig.get("caption_no_emoji"):
            add("Instagram", "instagram_no_emoji", "No-emoji variant", ig.get("caption_no_emoji", ""), ig)
    for i, tw in enumerate(data.get("twitter") or []):
        add("Twitter/X", f"twitter_{i+1}", tw.get("angle", ""), tw.get("text", ""), tw)
    v30 = data.get("video_30") or {}
    if v30:
        body = f"Hook:\n{v30.get('hook','')}\n\nBody:\n{v30.get('body','')}\n\nCTA:\n{v30.get('cta','')}"
        add("Video", "video_30s", "30-second script", body, v30)
    v60 = data.get("video_60") or {}
    if v60:
        body = f"Hook:\n{v60.get('hook','')}\n\nBody:\n{v60.get('body','')}\n\nCTA:\n{v60.get('cta','')}"
        add("Video", "video_60s", "60-second script", body, v60)
    em = data.get("email") or {}
    if em:
        body = f"Subject: {em.get('subject','')}\n\n{em.get('body','')}\n\nCTA: {em.get('cta','')}"
        add("Email", "email_newsletter", em.get("subject", "Email"), body, em)
    blog = data.get("blog_outline") or {}
    if blog:
        lines = [f"# {blog.get('h1','')}"]
        for sec in blog.get("sections") or []:
            lines.append(f"\n## {sec.get('h2','')}\n- " + "\n- ".join(sec.get("key_points") or []))
            lines.append(f"(~{sec.get('suggested_words',0)} words)")
        add("Blog", "blog_outline", blog.get("h1", "Outline"), "\n".join(lines), blog)
    for i, ad in enumerate(data.get("google_ads") or []):
        body = f"Headline: {ad.get('headline','')}\nDescription: {ad.get('description','')}"
        add("Google Ads", f"google_ad_{i+1}", ad.get("headline", f"Ad {i+1}"), body, ad)
    seo = data.get("seo") or {}
    if seo:
        body = f"Title: {seo.get('meta_title','')}\nMeta: {seo.get('meta_description','')}"
        add("SEO", "seo_meta", seo.get("meta_title", "SEO"), body, seo)

    # Topic line for all
    for p in pieces:
        if not p.title or p.title in ("Main",):
            p.title = topic[:120]
    return pieces


class ContentGenerateOut(BaseModel):
    generated: dict[str, Any]
    content_piece_ids: list[str]


@router.post("/generate", response_model=ContentGenerateOut)
async def generate(body: ContentGenerateIn, db: AsyncSession = Depends(get_db)):
    cr = await db.execute(
        select(Campaign, BrandProfile)
        .join(BrandProfile, Campaign.brand_id == BrandProfile.id)
        .where(Campaign.id == body.campaign_id)
    )
    row = cr.first()
    if not row:
        raise HTTPException(404, "Campaign not found")
    campaign, brand = row
    data = await generate_all_formats(_brand(brand), _camp(campaign), body.topic, body.brief)
    pieces = _flatten_generated(campaign.id, data, body.topic)
    for p in pieces:
        db.add(p)
    await db.commit()
    return {"generated": data, "content_piece_ids": [p.id for p in pieces]}


class ContentRegenerateOut(BaseModel):
    content_piece_id: str
    platform: str
    body: str


@router.post("/regenerate", response_model=ContentRegenerateOut)
async def regenerate(body: ContentRegenerateIn, db: AsyncSession = Depends(get_db)):
    cr = await db.execute(
        select(Campaign, BrandProfile)
        .join(BrandProfile, Campaign.brand_id == BrandProfile.id)
        .where(Campaign.id == body.campaign_id)
    )
    row = cr.first()
    if not row:
        raise HTTPException(404, "Campaign not found")
    campaign, brand = row
    existing: ContentPiece | None = None
    if body.content_piece_id:
        r = await db.execute(
            select(ContentPiece).where(
                ContentPiece.id == body.content_piece_id,
                ContentPiece.campaign_id == body.campaign_id,
            )
        )
        existing = r.scalar_one_or_none()
        if not existing:
            raise HTTPException(404, "Content piece not found")
    else:
        r = await db.execute(
            select(ContentPiece).where(
                ContentPiece.campaign_id == body.campaign_id,
                ContentPiece.format_key == body.format_key,
                ContentPiece.platform == body.platform,
            )
        )
        existing = r.scalars().first()
    platform = existing.platform if existing else body.platform
    fmt = existing.format_key if existing else body.format_key
    system = build_brand_system_prefix(_brand(brand), _camp(campaign)) + "\nRewrite the marketing copy. Output only the new copy text, no quotes."
    user = f"Platform: {platform}\nFormat: {fmt}\nInstruction: {body.instruction}\n\nCurrent:\n{body.current_text}"
    new_text = await complete_text(system, user, temperature=0.85)
    if existing:
        existing.body = new_text
        await db.commit()
        await db.refresh(existing)
        return {"content_piece_id": existing.id, "platform": existing.platform, "body": new_text}
    cp = ContentPiece(
        campaign_id=body.campaign_id,
        platform=body.platform,
        format_key=body.format_key,
        title="Regenerated",
        body=new_text,
        status="Draft",
    )
    db.add(cp)
    await db.commit()
    await db.refresh(cp)
    return {"content_piece_id": cp.id, "platform": cp.platform, "body": new_text}


@router.get("/campaign/{campaign_id}")
async def list_content(campaign_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(
        select(ContentPiece).where(ContentPiece.campaign_id == campaign_id).order_by(ContentPiece.created_at.asc())
    )
    items = r.scalars().all()
    return [
        {
            "id": x.id,
            "platform": x.platform,
            "format_key": x.format_key,
            "title": x.title,
            "body": x.body,
            "extra": x.extra,
            "status": x.status,
            "scheduled_date": str(x.scheduled_date) if x.scheduled_date else None,
            "attribution": x.attribution,
        }
        for x in items
    ]


@router.patch("/piece/{piece_id}/status")
async def patch_status(piece_id: str, status: str = Query(...), db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(ContentPiece).where(ContentPiece.id == piece_id))
    p = r.scalar_one_or_none()
    if not p:
        raise HTTPException(404, "Not found")
    p.status = status
    await db.commit()
    return {"ok": True}
