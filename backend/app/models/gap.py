"""Gap models."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class GapPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GapStatus(str, Enum):
    IDENTIFIED = "identified"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    WONT_FIX = "wont_fix"


class GapSource(str, Enum):
    SEARCH_QUERY = "search_query"
    SUPPORT_TICKET = "support_ticket"
    USER_FEEDBACK = "user_feedback"
    CONTENT_ANALYSIS = "content_analysis"
    MANUAL = "manual"


class Gap(BaseModel):
    """Knowledge gap model."""
    id: str
    title: str
    description: str
    topic: str
    priority: GapPriority = GapPriority.MEDIUM
    status: GapStatus = GapStatus.IDENTIFIED
    source: GapSource
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    search_queries: List[str] = Field(default_factory=list)
    ticket_count: int = 0
    impact_score: float = 0.0
    suggested_content: Optional[str] = None
    related_content_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class GapCreate(BaseModel):
    """Gap creation model."""
    title: str
    description: str
    topic: str
    priority: GapPriority = GapPriority.MEDIUM
    source: GapSource = GapSource.MANUAL
    tags: List[str] = Field(default_factory=list)


class GapResponse(Gap):
    """Gap response with metadata."""
    pass
