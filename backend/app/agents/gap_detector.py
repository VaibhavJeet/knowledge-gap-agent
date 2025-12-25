"""Gap Detector Agent - Identifies knowledge gaps from various sources."""

from typing import List, Dict, Any, Optional
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from app.core.llm import get_llm


class DetectedGap(BaseModel):
    """Detected knowledge gap."""
    title: str = Field(description="Short title for the gap")
    description: str = Field(description="Detailed description of what's missing")
    topic: str = Field(description="Topic category")
    priority: str = Field(description="Priority: critical, high, medium, low")
    evidence: List[str] = Field(description="Supporting evidence")
    search_queries: List[str] = Field(description="Related search queries")
    impact_score: float = Field(description="Impact score 0-1")
    suggested_content: str = Field(description="Brief outline of suggested content")


class GapDetectionResult(BaseModel):
    """Result of gap detection analysis."""
    gaps: List[DetectedGap] = Field(default_factory=list)
    analysis_summary: str = Field(description="Summary of the analysis")
    total_queries_analyzed: int = 0
    total_tickets_analyzed: int = 0
    coverage_score: float = 0.0


class GapDetectorAgent:
    """Agent that detects knowledge gaps from search queries and support tickets."""

    def __init__(self):
        self.llm = get_llm()
        self.parser = JsonOutputParser(pydantic_object=GapDetectionResult)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert knowledge base analyst specializing in identifying 
gaps in documentation and support content.

Your job is to analyze:
1. Search queries with zero or poor results
2. Support tickets about topics not covered in documentation
3. User feedback indicating missing information
4. Content that exists but is incomplete or outdated

For each gap you identify:
- Provide a clear, actionable title
- Explain what information is missing
- Assess priority based on frequency and user impact
- Suggest what content should be created

Prioritize gaps that:
- Affect many users (high query/ticket volume)
- Block critical user workflows
- Relate to core product features
- Have easy-to-create solutions

{format_instructions}"""),
            ("human", """Analyze the following data to identify knowledge gaps:

## Zero-Result Search Queries
{search_queries}

## Support Tickets Without Documentation
{support_tickets}

## User Feedback
{user_feedback}

## Existing Content (for reference)
{existing_content}

Identify all knowledge gaps and prioritize them.""")
        ])

    async def detect_from_searches(
        self,
        zero_result_queries: List[Dict[str, Any]],
        existing_content: List[str] = None
    ) -> GapDetectionResult:
        """Detect gaps from search queries with no results."""
        queries_text = "\n".join([
            f"- \"{q.get('query', q)}\" (count: {q.get('count', 1)})"
            for q in zero_result_queries[:50]
        ])

        chain = self.prompt | self.llm | self.parser
        result = await chain.ainvoke({
            "search_queries": queries_text or "No search data available",
            "support_tickets": "No ticket data provided",
            "user_feedback": "No feedback data provided",
            "existing_content": "\n".join(existing_content[:20]) if existing_content else "No existing content provided",
            "format_instructions": self.parser.get_format_instructions()
        })

        if isinstance(result, dict):
            result["total_queries_analyzed"] = len(zero_result_queries)
            return GapDetectionResult(**result)
        return result

    async def detect_from_tickets(
        self,
        support_tickets: List[Dict[str, Any]],
        existing_content: List[str] = None
    ) -> GapDetectionResult:
        """Detect gaps from support tickets."""
        tickets_text = "\n\n".join([
            f"Ticket: {t.get('subject', 'No subject')}\n"
            f"Category: {t.get('category', 'Unknown')}\n"
            f"Description: {t.get('description', '')[:300]}"
            for t in support_tickets[:30]
        ])

        chain = self.prompt | self.llm | self.parser
        result = await chain.ainvoke({
            "search_queries": "No search data provided",
            "support_tickets": tickets_text or "No ticket data available",
            "user_feedback": "No feedback data provided",
            "existing_content": "\n".join(existing_content[:20]) if existing_content else "No existing content provided",
            "format_instructions": self.parser.get_format_instructions()
        })

        if isinstance(result, dict):
            result["total_tickets_analyzed"] = len(support_tickets)
            return GapDetectionResult(**result)
        return result

    async def detect(
        self,
        search_queries: List[Dict[str, Any]] = None,
        support_tickets: List[Dict[str, Any]] = None,
        user_feedback: List[Dict[str, Any]] = None,
        existing_content: List[str] = None
    ) -> GapDetectionResult:
        """Detect gaps from all available sources."""
        queries_text = ""
        if search_queries:
            queries_text = "\n".join([
                f"- \"{q.get('query', q)}\" (count: {q.get('count', 1)})"
                for q in search_queries[:50]
            ])

        tickets_text = ""
        if support_tickets:
            tickets_text = "\n\n".join([
                f"Ticket: {t.get('subject', 'No subject')}\n"
                f"Description: {t.get('description', '')[:200]}"
                for t in support_tickets[:30]
            ])

        feedback_text = ""
        if user_feedback:
            feedback_text = "\n".join([
                f"- {f.get('feedback', f)}"
                for f in user_feedback[:20]
            ])

        chain = self.prompt | self.llm | self.parser
        result = await chain.ainvoke({
            "search_queries": queries_text or "No search data available",
            "support_tickets": tickets_text or "No ticket data available",
            "user_feedback": feedback_text or "No feedback data available",
            "existing_content": "\n".join(existing_content[:20]) if existing_content else "No existing content",
            "format_instructions": self.parser.get_format_instructions()
        })

        if isinstance(result, dict):
            result["total_queries_analyzed"] = len(search_queries) if search_queries else 0
            result["total_tickets_analyzed"] = len(support_tickets) if support_tickets else 0
            return GapDetectionResult(**result)
        return result
