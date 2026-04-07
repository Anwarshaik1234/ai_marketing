import enum
import uuid
from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class CampaignGoal(str, enum.Enum):
    awareness = "Awareness"
    lead_gen = "Lead Gen"
    retention = "Retention"
    product_launch = "Product Launch"


class ContentStatus(str, enum.Enum):
    draft = "Draft"
    ready = "Ready"
    scheduled = "Scheduled"
    published = "Published"


class AdVariantStatus(str, enum.Enum):
    testing = "Testing"
    winner = "Winner"
    rejected = "Rejected"


class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    brand_name: Mapped[str] = mapped_column(String(255))
    industry: Mapped[str] = mapped_column(String(255))
    audience_age: Mapped[str] = mapped_column(String(120), default="")
    audience_interests: Mapped[str] = mapped_column(Text, default="")
    audience_pain_points: Mapped[str] = mapped_column(Text, default="")
    brand_tones: Mapped[list] = mapped_column(JSON, default=list)  # max 3 strings
    keywords_include: Mapped[str] = mapped_column(Text, default="")
    keywords_avoid: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="brand")


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brand_profiles.id"))
    name: Mapped[str] = mapped_column(String(255))
    goal: Mapped[str] = mapped_column(String(64))
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    platforms: Mapped[list] = mapped_column(JSON, default=list)
    validation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    brand: Mapped["BrandProfile"] = relationship(back_populates="campaigns")
    content_pieces: Mapped[list["ContentPiece"]] = relationship(back_populates="campaign")


class ContentPiece(Base):
    __tablename__ = "content_pieces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"))
    platform: Mapped[str] = mapped_column(String(64))
    format_key: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(512), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    extra: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default=ContentStatus.draft.value)
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    attribution: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    campaign: Mapped["Campaign"] = relationship(back_populates="content_pieces")


class RepurposeJob(Base):
    __tablename__ = "repurpose_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    asset_name: Mapped[str] = mapped_column(String(255))
    asset_type: Mapped[str] = mapped_column(String(64))
    raw_text: Mapped[str] = mapped_column(Text)
    coverage_map: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    insights: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AdExperiment(Base):
    __tablename__ = "ad_experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product: Mapped[str] = mapped_column(Text)
    audience: Mapped[str] = mapped_column(Text)
    platform: Mapped[str] = mapped_column(String(64))
    goal: Mapped[str] = mapped_column(String(128))
    variants: Mapped[list] = mapped_column(JSON, default=list)
    ai_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SentimentReport(Base):
    __tablename__ = "sentiment_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    source_filename: Mapped[str] = mapped_column(String(255))
    summary: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
