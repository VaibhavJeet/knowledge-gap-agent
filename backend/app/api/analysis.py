"""Analysis API routes."""

from datetime import datetime
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.db_models import AnalysisReportDB, GapDB, FAQDB
from app.agents.orchestrator import KnowledgeGapOrchestrator

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/run")
async def run_analysis(
    search_queries: List[dict] = None,
    support_tickets: List[dict] = None,
    expected_topics: List[str] = None,
    generate_faqs: bool = True,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db)
):
    """Run full knowledge gap analysis."""
    # Create report record
    report_id = str(uuid.uuid4())
    db_report = AnalysisReportDB(
        id=report_id,
        report_type="full_analysis",
        status="running"
    )
    db.add(db_report)
    await db.commit()

    # Run analysis
    orchestrator = KnowledgeGapOrchestrator()
    result = await orchestrator.run_full_analysis(
        search_queries=search_queries or [],
        support_tickets=support_tickets or [],
        expected_topics=expected_topics or [],
        generate_faqs=generate_faqs
    )

    # Save gaps
    for gap in result.gaps:
        db_gap = GapDB(
            id=str(uuid.uuid4()),
            title=gap.title,
            description=gap.description,
            topic=gap.topic,
            priority=gap.priority,
            source="content_analysis",
            impact_score=gap.impact_score,
            suggested_content=gap.suggested_content
        )
        db.add(db_gap)

    # Save FAQs
    for faq in result.faqs:
        db_faq = FAQDB(
            id=str(uuid.uuid4()),
            question=faq.question,
            answer=faq.answer,
            category=faq.category,
            confidence_score=faq.confidence_score,
            status="pending_review"
        )
        db.add(db_faq)

    # Update report
    db_report.status = "completed"
    db_report.gaps_found = result.gaps_found
    db_report.faqs_generated = result.faqs_generated
    db_report.suggestions_created = result.suggestions_created
    db_report.coverage_after = result.coverage_score
    db_report.summary = result.summary
    db_report.completed_at = datetime.utcnow()

    await db.commit()

    return {
        "report_id": report_id,
        "status": "completed",
        "gaps_found": result.gaps_found,
        "faqs_generated": result.faqs_generated,
        "suggestions_created": result.suggestions_created,
        "summary": result.summary,
        "duration_seconds": result.duration_seconds
    }


@router.get("/reports")
async def list_reports(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """List analysis reports."""
    result = await db.execute(
        select(AnalysisReportDB)
        .order_by(AnalysisReportDB.created_at.desc())
        .limit(limit)
    )
    reports = result.scalars().all()

    return [{
        "id": r.id,
        "report_type": r.report_type,
        "status": r.status,
        "gaps_found": r.gaps_found,
        "faqs_generated": r.faqs_generated,
        "summary": r.summary,
        "created_at": r.created_at.isoformat(),
        "completed_at": r.completed_at.isoformat() if r.completed_at else None
    } for r in reports]


@router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get analysis report details."""
    result = await db.execute(
        select(AnalysisReportDB).where(AnalysisReportDB.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": report.id,
        "report_type": report.report_type,
        "status": report.status,
        "gaps_found": report.gaps_found,
        "faqs_generated": report.faqs_generated,
        "suggestions_created": report.suggestions_created,
        "coverage_before": report.coverage_before,
        "coverage_after": report.coverage_after,
        "summary": report.summary,
        "details": report.details,
        "created_at": report.created_at.isoformat(),
        "completed_at": report.completed_at.isoformat() if report.completed_at else None
    }
