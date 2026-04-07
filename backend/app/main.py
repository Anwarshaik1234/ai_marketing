from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import ads, bonus, brand, calendar, campaign, content, repurpose, sentiment


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(title="AI Marketing Intelligence & Content Engine", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brand.router)
app.include_router(campaign.router)
app.include_router(content.router)
app.include_router(repurpose.router)
app.include_router(ads.router)
app.include_router(sentiment.router)
app.include_router(calendar.router)
app.include_router(bonus.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
