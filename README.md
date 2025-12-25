# Knowledge Gap Agent

An AI-powered agent that analyzes knowledge bases, support data, and user queries to identify documentation gaps, auto-generate FAQs, and optimize content coverage. Built with LangChain, MCP (Model Context Protocol) integrations, and Next.js 15.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-orange.svg)

## Problem Statement

Organizations struggle with knowledge management:
- **Incomplete Documentation**: Critical topics missing from knowledge bases
- **Outdated Content**: Information becomes stale as products evolve
- **User Frustration**: Customers can't find answers to common questions
- **Reactive Approach**: Gaps only discovered after customer complaints
- **Manual Analysis**: Time-consuming to identify what's missing

## Solution

Knowledge Gap Agent provides intelligent knowledge base optimization:

1. **Gap Detection**: Analyzes search queries, support tickets, and user behavior to find missing content
2. **FAQ Generation**: Automatically creates FAQs from common questions and their answers
3. **Coverage Analysis**: Maps existing content against user needs
4. **Content Suggestions**: Recommends new articles and topics to address gaps
5. **Quality Scoring**: Evaluates content freshness, completeness, and relevance

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Next.js 15 Frontend                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │   Gap    │  │   FAQ    │  │ Coverage │  │     Content      │ │
│  │ Analysis │  │Generator │  │   Map    │  │   Suggestions    │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              │ REST API
┌─────────────────────────────▼───────────────────────────────────┐
│                     FastAPI Backend                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   LangChain Agent Core                       ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  ││
│  │  │    Gap      │  │    FAQ      │  │     Content         │  ││
│  │  │  Detector   │  │  Generator  │  │     Analyzer        │  ││
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    MCP Integrations                          ││
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────────────────┐ ││
│  │  │  CMS   │  │ Search │  │Support │  │      Database      │ ││
│  │  │  MCP   │  │  MCP   │  │  MCP   │  │        MCP         │ ││
│  │  └────────┘  └────────┘  └────────┘  └────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Remote LLM │    │  Local LLM   │    │   Vector DB  │
│ (OpenAI/etc) │    │   (Ollama)   │    │  (ChromaDB)  │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - High-performance async API framework
- **LangChain 0.3+** - Agent orchestration and NLP
- **LangGraph** - Multi-agent workflow coordination
- **ChromaDB** - Vector storage for semantic search
- **Pydantic** - Data validation

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **TailwindCSS** - Utility-first styling
- **Shadcn/UI** - Accessible components
- **React Query** - Server state management

### MCP Integrations
- **CMS MCP** - Content management system access
- **Search MCP** - Search analytics integration
- **Support MCP** - Support ticket data
- **Database MCP** - Gap and FAQ storage

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (optional)

### 1. Clone the repository
```bash
git clone https://github.com/VaibhavJeet/knowledge-gap-agent.git
cd knowledge-gap-agent
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### 4. Access the Application
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Configuration

### LLM Configuration

```env
# Remote LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4-turbo-preview

# Local LLM (Ollama)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### MCP Integrations

Configure in `config/mcp.yaml`:

```yaml
integrations:
  cms:
    enabled: true
    provider: contentful  # or strapi, notion
    api_key: ${CMS_API_KEY}

  search:
    enabled: true
    provider: algolia  # or elasticsearch
    app_id: ${ALGOLIA_APP_ID}
    api_key: ${ALGOLIA_API_KEY}

  support:
    enabled: true
    provider: zendesk  # or freshdesk, intercom
    api_key: ${SUPPORT_API_KEY}
```

## Features

### Gap Detection
- Search query analysis
- Zero-result query tracking
- Support ticket pattern mining
- User feedback analysis
- Competitive content comparison

### FAQ Generation
- Automatic Q&A extraction from tickets
- Similar question clustering
- Answer quality scoring
- Multi-language support
- Approval workflow

### Coverage Analysis
- Topic taxonomy mapping
- Content completeness scoring
- User journey coverage
- Search-to-content matching
- Freshness tracking

### Content Suggestions
- Priority-ranked recommendations
- Outline generation
- Source material compilation
- SEO optimization hints
- Related content linking

## API Reference

### Gaps
- `GET /api/gaps` - List identified gaps
- `GET /api/gaps/{id}` - Get gap details
- `POST /api/gaps/analyze` - Run gap analysis
- `PUT /api/gaps/{id}/status` - Update gap status

### FAQs
- `GET /api/faqs` - List generated FAQs
- `POST /api/faqs/generate` - Generate FAQs from data
- `PUT /api/faqs/{id}` - Update FAQ
- `POST /api/faqs/{id}/publish` - Publish FAQ

### Content
- `GET /api/content` - List knowledge base content
- `GET /api/content/coverage` - Get coverage report
- `POST /api/content/suggestions` - Get content suggestions

### Analysis
- `POST /api/analysis/run` - Run full analysis
- `GET /api/analysis/reports` - List analysis reports
- `GET /api/analysis/reports/{id}` - Get report details

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
