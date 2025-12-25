"""API routes."""

from app.api.gaps import router as gaps_router
from app.api.faqs import router as faqs_router
from app.api.content import router as content_router
from app.api.analysis import router as analysis_router

__all__ = ["gaps_router", "faqs_router", "content_router", "analysis_router"]
