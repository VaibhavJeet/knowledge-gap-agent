# Contributing to Knowledge Gap Agent

Thank you for your interest in contributing to Knowledge Gap Agent! This document provides guidelines and instructions for contributing.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Adding New Features](#adding-new-features)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md). We are committed to providing a welcoming and inclusive environment.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/knowledge-gap-agent.git
   cd knowledge-gap-agent
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/VaibhavJeet/knowledge-gap-agent.git
   ```

## Development Setup

### Backend (Python)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### Frontend (Next.js)

```bash
cd frontend
npm install
```

### Environment Configuration

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env.local
```

### Running Locally

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

## Making Changes

### Branch Naming Convention

- `feature/` - New features (e.g., `feature/add-trend-analysis`)
- `fix/` - Bug fixes (e.g., `fix/gap-detection-accuracy`)
- `docs/` - Documentation changes (e.g., `docs/update-api-reference`)
- `refactor/` - Code refactoring (e.g., `refactor/optimize-clustering`)

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(agents): add semantic gap clustering
fix(analyzer): improve content coverage calculation
docs(readme): update LLM configuration section
```

## Adding New Features

### Adding a New LangChain Agent

1. Create agent file in `backend/app/agents/`:
   ```python
   # backend/app/agents/new_agent.py
   from langchain.agents import AgentExecutor
   from langchain_core.prompts import ChatPromptTemplate
   from langchain_core.output_parsers import JsonOutputParser
   from app.core.llm import get_llm
   
   class NewAgent:
       def __init__(self):
           self.llm = get_llm()
           self.parser = JsonOutputParser()
           self.prompt = ChatPromptTemplate.from_messages([...])
       
       async def analyze(self, input_data: dict) -> dict:
           chain = self.prompt | self.llm | self.parser
           return await chain.ainvoke(input_data)
   ```

2. Register in `backend/app/agents/__init__.py`
3. Add API endpoint if needed
4. Write tests in `backend/tests/agents/`

### Adding a New MCP Integration

1. Create integration in `backend/app/mcp/`:
   ```python
   # backend/app/mcp/new_integration.py
   from app.mcp.base import BaseMCPIntegration
   
   class NewIntegration(BaseMCPIntegration):
       name = "new_integration"
       
       async def connect(self):
           # Connection logic
           pass
       
       async def execute(self, action: str, params: dict):
           # Execute MCP action
           pass
   ```

2. Add configuration schema in `config/mcp.yaml`
3. Register in `backend/app/mcp/__init__.py`
4. Document in `docs/mcp-development.md`

### Adding Frontend Components

1. Create component in `frontend/src/components/`:
   ```tsx
   // frontend/src/components/NewComponent.tsx
   'use client';
   
   interface NewComponentProps {
     // props
   }
   
   export function NewComponent({ ...props }: NewComponentProps) {
     return (
       // JSX
     );
   }
   ```

2. Export from `frontend/src/components/index.ts`
3. Add Storybook story if applicable

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/agents/test_gap_detector.py

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

### Linting

```bash
# Backend
cd backend
ruff check .
ruff format .
mypy app

# Frontend
cd frontend
npm run lint
npm run format
```

## Pull Request Process

1. **Update your fork**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature
   ```

3. **Make your changes** and commit

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature
   ```

5. **Create a Pull Request** on GitHub

### PR Requirements

- [ ] Tests pass (`pytest` / `npm test`)
- [ ] Linting passes (`ruff` / `eslint`)
- [ ] Documentation updated if needed
- [ ] Changelog entry added (for significant changes)
- [ ] PR description explains the changes

### Review Process

1. Automated checks must pass
2. At least one maintainer review required
3. Address review feedback
4. Maintainer merges when approved

## Questions?

- Open a [GitHub Issue](https://github.com/VaibhavJeet/knowledge-gap-agent/issues)
- Start a [Discussion](https://github.com/VaibhavJeet/knowledge-gap-agent/discussions)

Thank you for contributing!
