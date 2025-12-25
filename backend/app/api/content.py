"""Content API routes."""

from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.content import Content, ContentType
from app.models.db_models import ContentDB
from app.agents.orchestrator import KnowledgeGapOrchestrator

router = APIRouter(prefix="/content", tags=["content"])


@router.get("")
async def list_content(
    content_type: Optional[ContentType] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List knowledge base content."""
    query = select(ContentDB)

    if content_type:
        query = query.where(ContentDB.content_type == content_type.value)
    if category:
        query = query.where(ContentDB.category == category)

    query = query.order_by(ContentDB.last_updated.desc()).limit(limit)
    result = await db.execute(query)
    content = result.scalars().all()

    return [{
        "id": c.id,
        "title": c.title,
        "content_type": c.content_type,
        "category": c.category,
        "view_count": c.view_count,
        "freshness_score": c.freshness_score,
        "completeness_score": c.completeness_score,
        "last_updated": c.last_updated.isoformat()
    } for c in content]


@router.get("/coverage")
async def get_coverage_report(
    expected_topics: List[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get content coverage report."""
    result = await db.execute(select(ContentDB))
    content_list = result.scalars().all()

    if not expected_topics:
        # Use unique categories as topics
        expected_topics = list(set(c.category for c in content_list))

    content_data = [{
        "id": c.id,
        "title": c.title,
        "content": c.content[:500],
        "category": c.category
    } for c in content_list]

    orchestrator = KnowledgeGapOrchestrator()
    coverage = await orchestrator.content_analyzer.analyze_coverage(
        content_list=content_data,
        expected_topics=expected_topics
    )

    return {
        "total_topics": coverage.total_topics,
        "covered_topics": coverage.covered_topics,
        "coverage_percentage": coverage.coverage_percentage,
        "well_covered": coverage.well_covered,
        "partially_covered": coverage.partially_covered,
        "not_covered": coverage.not_covered,
        "recommendations": coverage.recommendations
    }


@router.post("/suggestions")
async def get_content_suggestions(
    gap_title: str,
    gap_description: str,
    db: AsyncSession = Depends(get_db)
):
    """Get content suggestions for a gap."""
    result = await db.execute(select(ContentDB.title).limit(20))
    existing = [r[0] for r in result.fetchall()]

    orchestrator = KnowledgeGapOrchestrator()
    suggestion = await orchestrator.content_analyzer.suggest_content(
        gap_title=gap_title,
        gap_description=gap_description,
        existing_content=existing
    )

    return {
        "title": suggestion.title,
        "summary": suggestion.summary,
        "outline": suggestion.outline,
        "priority": suggestion.priority,
        "target_audience": suggestion.target_audience,
        "estimated_effort": suggestion.estimated_effort,
        "seo_keywords": suggestion.seo_keywords
    }


@router.post("/quality")
async def analyze_content_quality(
    content_ids: List[str],
    db: AsyncSession = Depends(get_db)
):
    """Analyze quality of specified content."""
    result = await db.execute(
        select(ContentDB).where(ContentDB.id.in_(content_ids))
    )
    content_list = result.scalars().all()

    content_data = [{
        "id": c.id,
        "title": c.title,
        "content": c.content,
        "category": c.category,
        "last_updated": c.last_updated.isoformat()
    } for c in content_list]

    orchestrator = KnowledgeGapOrchestrator()
    analysis = await orchestrator.analyze_content_quality(content_data)

    return {
        "assessments": [{
            "content_id": a.content_id,
            "title": a.title,
            "overall_score": a.overall_score,
            "completeness_score": a.completeness_score,
            "clarity_score": a.clarity_score,
            "issues": a.issues,
            "improvements": a.improvements
        } for a in analysis.quality_assessments],
        "summary": analysis.summary
    }
