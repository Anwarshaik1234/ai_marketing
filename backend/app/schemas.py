from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class BrandCreate(BaseModel):
    brand_name: str
    industry: str
    audience_age: str = ""
    audience_interests: str = ""
    audience_pain_points: str = ""
    brand_tones: list[str] = Field(default_factory=list, min_length=3, max_length=3)
    keywords_include: str = ""
    keywords_avoid: str = ""


class BrandOut(BaseModel):
    id: str
    brand_name: str
    industry: str
    audience_age: str
    audience_interests: str
    audience_pain_points: str
    brand_tones: list[str]
    keywords_include: str
    keywords_avoid: str
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignCreate(BaseModel):
    brand_id: str
    name: str
    goal: str
    start_date: date | None = None
    end_date: date | None = None
    platforms: list[str] = Field(default_factory=list)


class CampaignOut(BaseModel):
    id: str
    brand_id: str
    name: str
    goal: str
    start_date: date | None
    end_date: date | None
    platforms: list[str]
    validation_notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignValidateOut(BaseModel):
    campaign: CampaignOut
    validation_notes: str
    suggestions: list[str]


class ContentGenerateIn(BaseModel):
    campaign_id: str
    topic: str
    brief: str = ""


class ContentRegenerateIn(BaseModel):
    campaign_id: str
    content_piece_id: str | None = None
    format_key: str = ""
    platform: str = ""
    current_text: str
    instruction: str = "Regenerate with fresh angle while keeping brand rules."

    @model_validator(mode="after")
    def require_keys_without_piece(self):
        if not self.content_piece_id and (not self.platform or not self.format_key):
            raise ValueError("platform and format_key are required when content_piece_id is omitted")
        return self


class RepurposeIn(BaseModel):
    campaign_id: str
    asset_name: str
    asset_type: str  # blog | podcast | webinar
    text: str


class AdLabIn(BaseModel):
    product: str
    audience: str
    platform: str
    goal: str


class AdVariantPatch(BaseModel):
    variant_id: str
    status: Literal["Testing", "Winner", "Rejected"]


class SentimentUploadMeta(BaseModel):
    text_column: str = "text"


class CalendarMoveIn(BaseModel):
    content_piece_id: str
    scheduled_date: date | None = None


class CalendarExportQuery(BaseModel):
    format: str = "csv"  # csv | pdf
