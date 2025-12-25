"""FAQ Generator Agent - Automatically generates FAQs from support data."""

from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from app.core.llm import get_llm


class GeneratedFAQ(BaseModel):
    """Generated FAQ entry."""
    question: str = Field(description="Clear, user-friendly question")
    answer: str = Field(description="Comprehensive, helpful answer")
    category: str = Field(description="FAQ category")
    confidence_score: float = Field(description="Confidence in answer quality 0-1")
    source_summary: str = Field(description="Brief summary of sources used")
    related_questions: List[str] = Field(description="Related questions to consider")
    tags: List[str] = Field(description="Relevant tags")


class FAQGenerationResult(BaseModel):
    """Result of FAQ generation."""
    faqs: List[GeneratedFAQ] = Field(default_factory=list)
    total_sources_analyzed: int = 0
    categories_covered: List[str] = Field(default_factory=list)
    generation_summary: str = ""


class FAQGeneratorAgent:
    """Agent that generates FAQs from support tickets and common queries."""

    def __init__(self):
        self.llm = get_llm()
        self.parser = JsonOutputParser(pydantic_object=FAQGenerationResult)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert FAQ writer who creates clear, helpful FAQ content 
from support ticket data and common user questions.

Your FAQs should:
1. Use natural, user-friendly language in questions
2. Provide comprehensive but concise answers
3. Include step-by-step instructions where appropriate
4. Anticipate follow-up questions
5. Be accurate based on the source material

For each FAQ:
- Phrase questions as users would ask them
- Structure answers for easy scanning (bullets, numbered lists)
- Include relevant context and prerequisites
- Suggest related questions users might have

Assign confidence scores based on:
- Quality and consistency of source data
- How well the answer addresses the question
- Completeness of the information

{format_instructions}"""),
            ("human", """Generate FAQs from the following support data:

## Support Tickets
{tickets}

## Common Search Queries
{queries}

## Existing Documentation (for reference)
{documentation}

Generate high-quality FAQs that address the most common user needs.""")
        ])

    async def generate_from_tickets(
        self,
        tickets: List[Dict[str, Any]],
        existing_docs: List[str] = None
    ) -> FAQGenerationResult:
        """Generate FAQs from support tickets."""
        # Group similar tickets
        tickets_text = "\n\n".join([
            f"Subject: {t.get('subject', 'No subject')}\n"
            f"Question: {t.get('description', '')[:300]}\n"
            f"Resolution: {t.get('resolution', 'Not provided')[:300]}"
            for t in tickets[:40]
        ])

        chain = self.prompt | self.llm | self.parser
        result = await chain.ainvoke({
            "tickets": tickets_text or "No ticket data available",
            "queries": "No query data provided",
            "documentation": "\n".join(existing_docs[:10]) if existing_docs else "No existing documentation",
            "format_instructions": self.parser.get_format_instructions()
        })

        if isinstance(result, dict):
            result["total_sources_analyzed"] = len(tickets)
            return FAQGenerationResult(**result)
        return result

    async def generate_from_queries(
        self,
        queries: List[Dict[str, Any]],
        documentation: List[Dict[str, Any]] = None
    ) -> FAQGenerationResult:
        """Generate FAQs from common search queries."""
        queries_text = "\n".join([
            f"- \"{q.get('query', q)}\" (asked {q.get('count', 1)} times)"
            for q in queries[:50]
        ])

        docs_text = ""
        if documentation:
            docs_text = "\n\n".join([
                f"Title: {d.get('title', 'Untitled')}\n"
                f"Content: {d.get('content', '')[:500]}"
                for d in documentation[:10]
            ])

        chain = self.prompt | self.llm | self.parser
        result = await chain.ainvoke({
            "tickets": "No ticket data provided",
            "queries": queries_text or "No query data available",
            "documentation": docs_text or "No existing documentation",
            "format_instructions": self.parser.get_format_instructions()
        })

        if isinstance(result, dict):
            result["total_sources_analyzed"] = len(queries)
            return FAQGenerationResult(**result)
        return result

    async def generate(
        self,
        tickets: List[Dict[str, Any]] = None,
        queries: List[Dict[str, Any]] = None,
        documentation: List[Dict[str, Any]] = None
    ) -> FAQGenerationResult:
        """Generate FAQs from all available sources."""
        tickets_text = ""
        if tickets:
            tickets_text = "\n\n".join([
                f"Subject: {t.get('subject', 'No subject')}\n"
                f"Question: {t.get('description', '')[:250]}\n"
                f"Resolution: {t.get('resolution', 'Not provided')[:250]}"
                for t in tickets[:30]
            ])

        queries_text = ""
        if queries:
            queries_text = "\n".join([
                f"- \"{q.get('query', q)}\" (count: {q.get('count', 1)})"
                for q in queries[:40]
            ])

        docs_text = ""
        if documentation:
            docs_text = "\n\n".join([
                f"Title: {d.get('title', 'Untitled')}\n"
                f"Content: {d.get('content', '')[:400]}"
                for d in documentation[:10]
            ])

        chain = self.prompt | self.llm | self.parser
        result = await chain.ainvoke({
            "tickets": tickets_text or "No ticket data available",
            "queries": queries_text or "No query data available",
            "documentation": docs_text or "No existing documentation",
            "format_instructions": self.parser.get_format_instructions()
        })

        if isinstance(result, dict):
            result["total_sources_analyzed"] = (len(tickets) if tickets else 0) + (len(queries) if queries else 0)
            return FAQGenerationResult(**result)
        return result

    async def improve_faq(
        self,
        question: str,
        current_answer: str,
        feedback: List[str] = None
    ) -> GeneratedFAQ:
        """Improve an existing FAQ based on feedback."""
        improve_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert FAQ editor. Improve the given FAQ based on feedback.

Make the answer:
- More clear and concise
- More comprehensive where needed
- Better structured for readability
- More accurate based on feedback

{format_instructions}"""),
            ("human", """Improve this FAQ:

Question: {question}
Current Answer: {current_answer}

Feedback:
{feedback}

Provide an improved version.""")
        ])

        single_parser = JsonOutputParser(pydantic_object=GeneratedFAQ)
        chain = improve_prompt | self.llm | single_parser

        result = await chain.ainvoke({
            "question": question,
            "current_answer": current_answer,
            "feedback": "\n".join(feedback) if feedback else "No specific feedback",
            "format_instructions": single_parser.get_format_instructions()
        })

        if isinstance(result, dict):
            return GeneratedFAQ(**result)
        return result
