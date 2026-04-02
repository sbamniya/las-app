"""FuzeBox AEOS Assess — Main Application Entry Point"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import init_db
from app.api import assessments, chat, scoring, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FuzeBox AI Readiness & Agentic ROI Platform — CAITO · GSTI · RAI · RAIA · RAW",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(assessments.router)
app.include_router(chat.router)
app.include_router(scoring.router)
app.include_router(reports.router)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "frameworks": ["CAITO", "GSTI", "RAI", "RAIA", "RAW"],
        "description": "FuzeBox AI Readiness & Agentic ROI Platform",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
