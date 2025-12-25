"""FAQs API routes."""

from datetime import datetime
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.faq import FAQ, FAQCreate, FAQResponse, FAQStatus
from app.models.db_models import FAQDB
from app.agents.orchestrator import KnowledgeGapOrchestrator

router = APIRouter(prefix="/faqs", tags=["faqs"])


@router.get("", response_model=List[FAQResponse])
async def list_faqs(
    status: Optional[FAQStatus] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List FAQs."""
    query = select(FAQDB)

    if status:
        query = query.where(FAQDB.status == status.value)
    if category:
        query = query.where(FAQDB.category == category)

    query = query.order_by(FAQDB.created_at.desc()).limit(limit)
    result = await db.execute(query)
    faqs = result.scalars().all()

    return [_faq_to_response(f) for f in faqs]


@router.get("/{faq_id}", response_model=FAQResponse)
async def get_faq(faq_id: str, db: AsyncSession = Depends(get_db)):
    """Get FAQ details."""
    result = await db.execute(select(FAQDB).where(FAQDB.id == faq_id))
    faq = result.scalar_one_or_none()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return _faq_to_response(faq)


@router.post("", response_model=FAQResponse)
async def create_faq(faq: FAQCreate, db: AsyncSession = Depends(get_db)):
    """Create a FAQ manually."""
    db_faq = FAQDB(
        id=str(uuid.uuid4()),
        question=faq.question,
        answer=faq.answer,
        category=faq.category,
        tags=faq.tags
    )
    db.add(db_faq)
    await db.commit()
    await db.refresh(db_faq)
    return _faq_to_response(db_faq)


@router.post("/generate")
async def generate_faqs(
    support_tickets: List[dict] = None,
    search_queries: List[dict] = None,
    db: AsyncSession = Depends(get_db)
):
    """Generate FAQs from data."""
    orchestrator = KnowledgeGapOrchestrator()
    result = await orchestrator.generate_faqs_only(
        support_tickets=support_tickets or [],
        search_queries=search_queries or []
    )

    # Save generated FAQs
    saved_faqs = []
    for faq in result.faqs:
        db_faq = FAQDB(
            id=str(uuid.uuid4()),
            question=faq.question,
            answer=faq.answer,
            category=faq.category,
            confidence_score=faq.confidence_score,
            source_queries=faq.related_questions,
            tags=faq.tags,
            status="pending_review"
        )
        db.add(db_faq)
        saved_faqs.append(db_faq)

    await db.commit()

    return {
        "faqs_generated": len(result.faqs),
        "categories": result.categories_covered,
        "summary": result.generation_summary
    }


@router.put("/{faq_id}")
async def update_faq(
    faq_id: str,
    updates: dict,
    db: AsyncSession = Depends(get_db)
):
    """Update a FAQ."""
    result = await db.execute(select(FAQDB).where(FAQDB.id == faq_id))
    faq = result.scalar_one_or_none()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    allowed = ["question", "answer", "category", "tags", "status"]
    for field in allowed:
        if field in updates:
            setattr(faq, field, updates[field])

    faq.updated_at = datetime.utcnow()
    await db.commit()

    return {"updated": True, "faq_id": faq_id}


@router.post("/{faq_id}/publish")
async def publish_faq(faq_id: str, db: AsyncSession = Depends(get_db)):
    """Publish a FAQ."""
    result = await db.execute(select(FAQDB).where(FAQDB.id == faq_id))
    faq = result.scalar_one_or_none()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    faq.status = "published"
    faq.published_at = datetime.utcnow()
    faq.updated_at = datetime.utcnow()
    await db.commit()

    return {"published": True, "faq_id": faq_id}


@router.post("/{faq_id}/feedback")
async def faq_feedback(
    faq_id: str,
    helpful: bool,
    db: AsyncSession = Depends(get_db)
):
    """Record FAQ helpfulness feedback."""
    result = await db.execute(select(FAQDB).where(FAQDB.id == faq_id))
    faq = result.scalar_one_or_none()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    if helpful:
        faq.helpful_count += 1
    else:
        faq.not_helpful_count += 1

    await db.commit()
    return {"recorded": True}


@router.delete("/{faq_id}")
async def delete_faq(faq_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a FAQ."""
    result = await db.execute(select(FAQDB).where(FAQDB.id == faq_id))
    faq = result.scalar_one_or_none()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    await db.delete(faq)
    await db.commit()
    return {"deleted": True}


def _faq_to_response(faq: FAQDB) -> FAQResponse:
    total_votes = faq.helpful_count + faq.not_helpful_count
    helpfulness = faq.helpful_count / total_votes if total_votes > 0 else None

    return FAQResponse(
        id=faq.id,
        question=faq.question,
        answer=faq.answer,
        category=faq.category,
        status=FAQStatus(faq.status),
        source_tickets=faq.source_tickets or [],
        source_queries=faq.source_queries or [],
        confidence_score=faq.confidence_score,
        view_count=faq.view_count,
        helpful_count=faq.helpful_count,
        not_helpful_count=faq.not_helpful_count,
        related_faqs=faq.related_faqs or [],
        tags=faq.tags or [],
        created_at=faq.created_at,
        updated_at=faq.updated_at,
        published_at=faq.published_at,
        helpfulness_ratio=helpfulness
    )
