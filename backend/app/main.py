"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import gaps_router, faqs_router, content_router, analysis_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description="AI-powered knowledge gap detection, FAQ generation, and content optimization",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gaps_router, prefix=settings.api_prefix)
app.include_router(faqs_router, prefix=settings.api_prefix)
app.include_router(content_router, prefix=settings.api_prefix)
app.include_router(analysis_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    return {"name": settings.app_name, "version": "0.1.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "llm_provider": settings.llm_provider}
