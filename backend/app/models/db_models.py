"""SQLAlchemy database models."""

from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, JSON, Enum as SQLEnum
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class GapDB(Base):
    """Gap database model."""
    __tablename__ = "gaps"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    topic = Column(String, nullable=False, index=True)
    priority = Column(String, default="medium")
    status = Column(String, default="identified")
    source = Column(String, nullable=False)
    evidence = Column(JSON, default=list)
    search_queries = Column(JSON, default=list)
    ticket_count = Column(Integer, default=0)
    impact_score = Column(Float, default=0.0)
    suggested_content = Column(Text, nullable=True)
    related_content_ids = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FAQDB(Base):
    """FAQ database model."""
    __tablename__ = "faqs"

    id = Column(String, primary_key=True, default=generate_uuid)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String, nullable=False, index=True)
    status = Column(String, default="draft")
    source_tickets = Column(JSON, default=list)
    source_queries = Column(JSON, default=list)
    confidence_score = Column(Float, default=0.0)
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    related_faqs = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)


class ContentDB(Base):
    """Content database model."""
    __tablename__ = "content"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String, nullable=False)
    url = Column(String, nullable=True)
    category = Column(String, nullable=False, index=True)
    tags = Column(JSON, default=list)
    view_count = Column(Integer, default=0)
    search_hits = Column(Integer, default=0)
    helpful_votes = Column(Integer, default=0)
    freshness_score = Column(Float, default=1.0)
    completeness_score = Column(Float, default=0.0)
    embedding = Column(JSON, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalysisReportDB(Base):
    """Analysis report database model."""
    __tablename__ = "analysis_reports"

    id = Column(String, primary_key=True, default=generate_uuid)
    report_type = Column(String, nullable=False)
    status = Column(String, default="running")
    gaps_found = Column(Integer, default=0)
    faqs_generated = Column(Integer, default=0)
    suggestions_created = Column(Integer, default=0)
    coverage_before = Column(Float, nullable=True)
    coverage_after = Column(Float, nullable=True)
    summary = Column(Text, nullable=True)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
