"""Content models."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ContentType(str, Enum):
    ARTICLE = "article"
    FAQ = "faq"
    GUIDE = "guide"
    TUTORIAL = "tutorial"
    REFERENCE = "reference"


class Content(BaseModel):
    """Knowledge base content model."""
    id: str
    title: str
    content: str
    content_type: ContentType
    url: Optional[str] = None
    category: str
    tags: List[str] = Field(default_factory=list)
    view_count: int = 0
    search_hits: int = 0
    helpful_votes: int = 0
    freshness_score: float = 1.0
    completeness_score: float = 0.0
    last_updated: datetime
    created_at: datetime


class ContentSuggestion(BaseModel):
    """Content suggestion for addressing gaps."""
    id: str
    gap_id: str
    title: str
    outline: List[str] = Field(default_factory=list)
    summary: str
    priority: str = "medium"
    estimated_effort: str = "medium"
    target_audience: str
    related_content: List[str] = Field(default_factory=list)
    seo_keywords: List[str] = Field(default_factory=list)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime


class CoverageReport(BaseModel):
    """Content coverage analysis report."""
    total_topics: int
    covered_topics: int
    coverage_percentage: float
    gaps_by_category: Dict[str, int] = Field(default_factory=dict)
    top_missing_topics: List[str] = Field(default_factory=list)
    stale_content_count: int = 0
    low_quality_count: int = 0
    recommendations: List[str] = Field(default_factory=list)
