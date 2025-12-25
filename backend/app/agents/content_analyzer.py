"""Content Analyzer Agent - Analyzes existing content for quality and coverage."""

from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from app.core.llm import get_llm


class ContentQuality(BaseModel):
    """Content quality assessment."""
    content_id: str
    title: str
    completeness_score: float = Field(description="Completeness 0-1")
    clarity_score: float = Field(description="Clarity 0-1")
    accuracy_score: float = Field(description="Accuracy 0-1")
    freshness_score: float = Field(description="Freshness 0-1")
    overall_score: float = Field(description="Overall quality 0-1")
    issues: List[str] = Field(description="Identified issues")
    improvements: List[str] = Field(description="Suggested improvements")


class CoverageAnalysis(BaseModel):
    """Content coverage analysis."""
    total_topics: int
    covered_topics: int
    coverage_percentage: float
    well_covered: List[str] = Field(description="Well-covered topics")
    partially_covered: List[str] = Field(description="Partially covered topics")
    not_covered: List[str] = Field(description="Missing topics")
    recommendations: List[str] = Field(description="Coverage recommendations")


class ContentSuggestionOutput(BaseModel):
    """Suggested content to create."""
    title: str
    summary: str
    outline: List[str] = Field(description="Content outline sections")
    priority: str
    target_audience: str
    estimated_effort: str
    seo_keywords: List[str] = Field(default_factory=list)
    related_content: List[str] = Field(default_factory=list)


class ContentAnalysisResult(BaseModel):
    """Result of content analysis."""
    quality_assessments: List[ContentQuality] = Field(default_factory=list)
    coverage: Optional[CoverageAnalysis] = None
    suggestions: List[ContentSuggestionOutput] = Field(default_factory=list)
    summary: str = ""


class ContentAnalyzerAgent:
    """Agent that analyzes content quality and coverage."""

    def __init__(self):
        self.llm = get_llm()
        self.quality_parser = JsonOutputParser(pydantic_object=ContentQuality)
        self.coverage_parser = JsonOutputParser(pydantic_object=CoverageAnalysis)
        self.suggestion_parser = JsonOutputParser(pydantic_object=ContentSuggestionOutput)

    async def analyze_quality(
        self,
        content: Dict[str, Any]
    ) -> ContentQuality:
        """Analyze quality of a single piece of content."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a content quality analyst. Evaluate the given content on:

1. **Completeness**: Does it cover the topic thoroughly?
2. **Clarity**: Is it easy to understand?
3. **Accuracy**: Is the information correct and current?
4. **Freshness**: Is it up-to-date?

Score each dimension 0-1 and identify specific issues and improvements.

{format_instructions}"""),
            ("human", """Analyze this content:

Title: {title}
Content: {content}
Last Updated: {last_updated}
Category: {category}

Provide a quality assessment.""")
        ])

        chain = prompt | self.llm | self.quality_parser
        result = await chain.ainvoke({
            "title": content.get("title", "Untitled"),
            "content": content.get("content", "")[:3000],
            "last_updated": content.get("last_updated", "Unknown"),
            "category": content.get("category", "Unknown"),
            "format_instructions": self.quality_parser.get_format_instructions()
        })

        if isinstance(result, dict):
            result["content_id"] = content.get("id", "")
            result["title"] = content.get("title", "Untitled")
            return ContentQuality(**result)
        return result

    async def analyze_coverage(
        self,
        content_list: List[Dict[str, Any]],
        expected_topics: List[str]
    ) -> CoverageAnalysis:
        """Analyze content coverage against expected topics."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a content coverage analyst. Compare existing content 
against expected topics to identify gaps.

For each expected topic, determine if it is:
- Well covered: Comprehensive content exists
- Partially covered: Some content but incomplete
- Not covered: No content addresses this topic

Provide actionable recommendations for improving coverage.

{format_instructions}"""),
            ("human", """Analyze coverage:

## Existing Content
{existing_content}

## Expected Topics to Cover
{expected_topics}

Provide a coverage analysis.""")
        ])

        content_summary = "\n".join([
            f"- {c.get('title', 'Untitled')}: {c.get('content', '')[:200]}..."
            for c in content_list[:30]
        ])

        chain = prompt | self.llm | self.coverage_parser
        result = await chain.ainvoke({
            "existing_content": content_summary,
            "expected_topics": "\n".join([f"- {t}" for t in expected_topics]),
            "format_instructions": self.coverage_parser.get_format_instructions()
        })

        if isinstance(result, dict):
            return CoverageAnalysis(**result)
        return result

    async def suggest_content(
        self,
        gap_title: str,
        gap_description: str,
        existing_content: List[str] = None
    ) -> ContentSuggestionOutput:
        """Generate content suggestion for a gap."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a content strategist. Create a detailed content 
suggestion to address a knowledge gap.

Provide:
1. A compelling title
2. A summary of what to cover
3. A detailed outline with sections
4. Priority and effort assessment
5. SEO keywords to target
6. Related content to link to

{format_instructions}"""),
            ("human", """Create a content suggestion for this gap:

Gap Title: {gap_title}
Gap Description: {gap_description}

Existing Related Content:
{existing_content}

Provide a comprehensive content suggestion.""")
        ])

        chain = prompt | self.llm | self.suggestion_parser
        result = await chain.ainvoke({
            "gap_title": gap_title,
            "gap_description": gap_description,
            "existing_content": "\n".join(existing_content[:10]) if existing_content else "No related content",
            "format_instructions": self.suggestion_parser.get_format_instructions()
        })

        if isinstance(result, dict):
            return ContentSuggestionOutput(**result)
        return result
