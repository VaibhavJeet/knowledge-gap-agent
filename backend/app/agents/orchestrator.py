"""Knowledge Gap Orchestrator - Coordinates all agents."""

from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
import time

from app.agents.gap_detector import GapDetectorAgent, GapDetectionResult
from app.agents.faq_generator import FAQGeneratorAgent, FAQGenerationResult
from app.agents.content_analyzer import ContentAnalyzerAgent, ContentAnalysisResult


class AnalysisReport:
    """Complete analysis report."""
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.gaps_found = 0
        self.faqs_generated = 0
        self.suggestions_created = 0
        self.coverage_score = 0.0
        self.gaps = []
        self.faqs = []
        self.suggestions = []
        self.summary = ""
        self.created_at = datetime.utcnow()
        self.duration_seconds = 0.0


class KnowledgeGapOrchestrator:
    """Orchestrates the complete knowledge gap analysis workflow."""

    def __init__(self, mcp_integrations: Optional[Dict[str, Any]] = None):
        self.gap_detector = GapDetectorAgent()
        self.faq_generator = FAQGeneratorAgent()
        self.content_analyzer = ContentAnalyzerAgent()
        self.mcp = mcp_integrations or {}

    async def run_full_analysis(
        self,
        search_queries: List[Dict[str, Any]] = None,
        support_tickets: List[Dict[str, Any]] = None,
        user_feedback: List[Dict[str, Any]] = None,
        existing_content: List[Dict[str, Any]] = None,
        expected_topics: List[str] = None,
        generate_faqs: bool = True,
        generate_suggestions: bool = True
    ) -> AnalysisReport:
        """Run complete knowledge gap analysis."""
        start_time = time.time()
        report = AnalysisReport()

        # Step 1: Detect gaps
        content_titles = [c.get("title", "") for c in existing_content] if existing_content else []
        gap_result = await self.gap_detector.detect(
            search_queries=search_queries,
            support_tickets=support_tickets,
            user_feedback=user_feedback,
            existing_content=content_titles
        )
        
        report.gaps = gap_result.gaps
        report.gaps_found = len(gap_result.gaps)

        # Step 2: Analyze coverage if topics provided
        if expected_topics and existing_content:
            coverage = await self.content_analyzer.analyze_coverage(
                content_list=existing_content,
                expected_topics=expected_topics
            )
            report.coverage_score = coverage.coverage_percentage

        # Step 3: Generate FAQs from tickets
        if generate_faqs and support_tickets:
            faq_result = await self.faq_generator.generate(
                tickets=support_tickets,
                queries=search_queries,
                documentation=existing_content
            )
            report.faqs = faq_result.faqs
            report.faqs_generated = len(faq_result.faqs)

        # Step 4: Generate content suggestions for gaps
        if generate_suggestions:
            for gap in gap_result.gaps[:5]:  # Top 5 gaps
                suggestion = await self.content_analyzer.suggest_content(
                    gap_title=gap.title,
                    gap_description=gap.description,
                    existing_content=content_titles[:10]
                )
                report.suggestions.append(suggestion)
            report.suggestions_created = len(report.suggestions)

        # Generate summary
        report.summary = self._generate_summary(report, gap_result)
        report.duration_seconds = time.time() - start_time

        return report

    async def detect_gaps_only(
        self,
        search_queries: List[Dict[str, Any]] = None,
        support_tickets: List[Dict[str, Any]] = None,
        existing_content: List[str] = None
    ) -> GapDetectionResult:
        """Run gap detection only."""
        return await self.gap_detector.detect(
            search_queries=search_queries,
            support_tickets=support_tickets,
            existing_content=existing_content
        )

    async def generate_faqs_only(
        self,
        support_tickets: List[Dict[str, Any]] = None,
        search_queries: List[Dict[str, Any]] = None
    ) -> FAQGenerationResult:
        """Generate FAQs only."""
        return await self.faq_generator.generate(
            tickets=support_tickets,
            queries=search_queries
        )

    async def analyze_content_quality(
        self,
        content_list: List[Dict[str, Any]]
    ) -> ContentAnalysisResult:
        """Analyze content quality."""
        result = ContentAnalysisResult()
        
        for content in content_list[:20]:
            quality = await self.content_analyzer.analyze_quality(content)
            result.quality_assessments.append(quality)

        # Calculate summary
        if result.quality_assessments:
            avg_score = sum(q.overall_score for q in result.quality_assessments) / len(result.quality_assessments)
            result.summary = f"Analyzed {len(result.quality_assessments)} pieces of content. Average quality score: {avg_score:.2f}"

        return result

    def _generate_summary(self, report: AnalysisReport, gap_result: GapDetectionResult) -> str:
        """Generate analysis summary."""
        parts = [
            f"Analysis completed in {report.duration_seconds:.1f} seconds.",
            f"Identified {report.gaps_found} knowledge gaps.",
        ]

        if report.faqs_generated:
            parts.append(f"Generated {report.faqs_generated} FAQs.")

        if report.suggestions_created:
            parts.append(f"Created {report.suggestions_created} content suggestions.")

        if report.coverage_score:
            parts.append(f"Current coverage: {report.coverage_score:.1f}%.")

        # Highlight critical gaps
        critical_gaps = [g for g in report.gaps if g.priority == "critical"]
        if critical_gaps:
            parts.append(f"ATTENTION: {len(critical_gaps)} critical gaps require immediate attention.")

        return " ".join(parts)
