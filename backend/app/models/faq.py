"""FAQ models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class FAQStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class FAQ(BaseModel):
    """FAQ model."""
    id: str
    question: str
    answer: str
    category: str
    status: FAQStatus = FAQStatus.DRAFT
    source_tickets: List[str] = Field(default_factory=list)
    source_queries: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0
    view_count: int = 0
    helpful_count: int = 0
    not_helpful_count: int = 0
    related_faqs: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None


class FAQCreate(BaseModel):
    """FAQ creation model."""
    question: str
    answer: str
    category: str
    tags: List[str] = Field(default_factory=list)


class FAQResponse(FAQ):
    """FAQ response with metadata."""
    helpfulness_ratio: Optional[float] = None
