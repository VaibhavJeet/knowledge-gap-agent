"""Gaps API routes."""

from datetime import datetime
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.gap import Gap, GapCreate, GapResponse, GapStatus, GapPriority
from app.models.db_models import GapDB
from app.agents.orchestrator import KnowledgeGapOrchestrator

router = APIRouter(prefix="/gaps", tags=["gaps"])


@router.get("", response_model=List[GapResponse])
async def list_gaps(
    status: Optional[GapStatus] = Query(None),
    priority: Optional[GapPriority] = Query(None),
    topic: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List identified knowledge gaps."""
    query = select(GapDB)

    if status:
        query = query.where(GapDB.status == status.value)
    if priority:
        query = query.where(GapDB.priority == priority.value)
    if topic:
        query = query.where(GapDB.topic.ilike(f"%{topic}%"))

    query = query.order_by(GapDB.impact_score.desc()).limit(limit)
    result = await db.execute(query)
    gaps = result.scalars().all()

    return [_gap_to_response(g) for g in gaps]


@router.get("/{gap_id}", response_model=GapResponse)
async def get_gap(gap_id: str, db: AsyncSession = Depends(get_db)):
    """Get gap details."""
    result = await db.execute(select(GapDB).where(GapDB.id == gap_id))
    gap = result.scalar_one_or_none()
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")
    return _gap_to_response(gap)


@router.post("", response_model=GapResponse)
async def create_gap(gap: GapCreate, db: AsyncSession = Depends(get_db)):
    """Create a gap manually."""
    db_gap = GapDB(
        id=str(uuid.uuid4()),
        title=gap.title,
        description=gap.description,
        topic=gap.topic,
        priority=gap.priority.value,
        source=gap.source.value,
        tags=gap.tags
    )
    db.add(db_gap)
    await db.commit()
    await db.refresh(db_gap)
    return _gap_to_response(db_gap)


@router.post("/analyze")
async def analyze_gaps(
    search_queries: List[dict] = None,
    support_tickets: List[dict] = None,
    db: AsyncSession = Depends(get_db)
):
    """Run gap analysis on provided data."""
    orchestrator = KnowledgeGapOrchestrator()
    result = await orchestrator.detect_gaps_only(
        search_queries=search_queries or [],
        support_tickets=support_tickets or []
    )

    # Save detected gaps
    saved_gaps = []
    for gap in result.gaps:
        db_gap = GapDB(
            id=str(uuid.uuid4()),
            title=gap.title,
            description=gap.description,
            topic=gap.topic,
            priority=gap.priority,
            source="content_analysis",
            evidence=gap.evidence,
            search_queries=gap.search_queries,
            impact_score=gap.impact_score,
            suggested_content=gap.suggested_content
        )
        db.add(db_gap)
        saved_gaps.append(db_gap)

    await db.commit()

    return {
        "gaps_found": len(result.gaps),
        "summary": result.analysis_summary,
        "coverage_score": result.coverage_score
    }


@router.put("/{gap_id}/status")
async def update_gap_status(
    gap_id: str,
    status: GapStatus,
    db: AsyncSession = Depends(get_db)
):
    """Update gap status."""
    result = await db.execute(select(GapDB).where(GapDB.id == gap_id))
    gap = result.scalar_one_or_none()
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")

    gap.status = status.value
    gap.updated_at = datetime.utcnow()
    await db.commit()

    return {"updated": True, "gap_id": gap_id, "status": status.value}


@router.delete("/{gap_id}")
async def delete_gap(gap_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a gap."""
    result = await db.execute(select(GapDB).where(GapDB.id == gap_id))
    gap = result.scalar_one_or_none()
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")

    await db.delete(gap)
    await db.commit()
    return {"deleted": True, "gap_id": gap_id}


def _gap_to_response(gap: GapDB) -> GapResponse:
    return GapResponse(
        id=gap.id,
        title=gap.title,
        description=gap.description,
        topic=gap.topic,
        priority=GapPriority(gap.priority),
        status=GapStatus(gap.status),
        source=gap.source,
        evidence=gap.evidence or [],
        search_queries=gap.search_queries or [],
        ticket_count=gap.ticket_count,
        impact_score=gap.impact_score,
        suggested_content=gap.suggested_content,
        related_content_ids=gap.related_content_ids or [],
        tags=gap.tags or [],
        created_at=gap.created_at,
        updated_at=gap.updated_at
    )
