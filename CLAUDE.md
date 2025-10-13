# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CodeRabbit is an AI-powered code review system that analyzes pull requests using a multi-agent AI architecture. The system combines:
- AST (Abstract Syntax Tree) parsing for code structure analysis
- Vector database (Qdrant) for storing code embeddings, relationships, and learnings
- Multi-agent AI system using LangGraph with Google Gemini
- GitHub webhook integration for automated PR analysis

## Architecture

### Multi-Agent Review System
The core review system uses **LangGraph** to orchestrate specialized agents in parallel:

1. **Context Fetcher Agent** (entry point): Retrieves vector database context for changed files
2. **Security Analysis Agent**: Analyzes security vulnerabilities in parallel
3. **Code Quality Agent**: Reviews code quality, best practices in parallel
4. **Performance Agent**: Checks for performance issues in parallel
5. **Aggregator Agent**: Combines all agent outputs into final review

**Agent Flow** (`src/agents/graph.py`):
- Context fetcher runs first and fans out to 3 parallel agents
- Agents use conditional edges to wait until all 3 complete
- Aggregator combines results and generates final review
- State is managed through `CodeReviewState` TypedDict with agent status tracking

### Core Components
- **Vector Database**: Qdrant with 3 collections:
  - `code_graphs`: AST-based code structure (functions, classes, relationships)
  - `import_files`: Source code and import dependencies
  - `learnings`: Historical review feedback for continuous improvement

- **AST Parser** (`src/services/simple_ast_parser.py`): Uses tree-sitter for Python, JavaScript, TypeScript, Go, Rust

- **Context Builder** (`src/services/simple_context_builder.py`): Combines git diffs, PR history, and code analysis

- **Vector Retriever** (`src/services/vector_retriever.py`): Fetches relevant code graphs, imports, and learnings from Qdrant

### Key Modules
- `src/ai/multi_agent_reviewer.py`: Multi-agent review orchestration
- `src/agents/`: LangGraph agent definitions (nodes, state, prompts, graph)
- `src/db/`: Vector database indexing and embedding services
- `src/services/`: AST parsing, context building, history fetching, vector retrieval
- `src/webhook/github_webhook.py`: GitHub webhook handling and pipeline orchestration
- `src/git_ops/`: Git repository cloning and diff extraction
- `src/utils/`: Configuration, GitHub bot, Qdrant client

## Development Commands

All commands should be run from the `backend/` directory.

### Environment Setup
```bash
cd backend
uv sync                    # Install dependencies
source .venv/bin/activate  # Optional: activate virtual environment
```

### Running the Application
```bash
uv run python main.py                                      # Start FastAPI server (recommended)
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload  # Alternative with uvicorn directly
```

### Development Tools
```bash
uv run ruff check .        # Linting
uv run black .             # Code formatting
uv run bandit -r src/      # Security checks
uv run pytest              # Run tests
```

### Application Startup Sequence
On server startup (`main.py`), the following initialization occurs:
1. Vector database collections are created (`initialize_collections()`)
2. Embedding model loads (`BAAI/bge-small-en-v1.5`)
3. `VectorIndexer` is initialized and attached to `app.state`
4. Services become available for webhook requests

## Key Workflows

### PR Analysis Pipeline (`src/webhook/github_webhook.py`)
The webhook handler orchestrates the entire analysis pipeline:

1. **Webhook Reception**: GitHub sends PR event to `/api/webhook`
2. **Signature Verification**: HMAC validation using `GITHUB_WEBHOOK_SECRET`
3. **Repository Setup**: Clone repo to `temp_repos/` and checkout PR branches
4. **Diff Extraction**: Get diff between base and head branches
5. **AST Parsing & Indexing**:
   - Parse changed `.py` files with tree-sitter
   - Build code graphs and extract imports
   - Index to Qdrant (`code_graphs` and `import_files` collections)
6. **Context Building**:
   - Fetch PR history (commits, comments) via `HistoryFetcher`
   - Build comprehensive context via `SimpleContextBuilder`
   - Save context to `ai_context_{pr_number}_{timestamp}.md` for debugging
7. **Multi-Agent Review**:
   - Execute LangGraph workflow (`review_code_with_multi_agents`)
   - Agents run in parallel and aggregate results
8. **Learning Indexing**: Index bot reviews + user feedback to `learnings` collection
9. **GitHub Comment**: Post review via GitHub App bot

### Learning System
The system learns from maintainer feedback:
- **Bot reviews + user replies**: Direct feedback on bot suggestions
- **Maintainer reviews**: Expert human reviews (with or without bot context)
- **Learning storage**: Indexed in Qdrant for future context retrieval
- **Continuous improvement**: Past learnings inform future reviews

## Configuration

Required environment variables (see `.env` file):
- `GITHUB_WEBHOOK_SECRET`: Webhook signature verification
- `GEMINI_API_KEY`: Google Gemini API key for AI agents
- GitHub App credentials for posting bot comments

## Important Implementation Notes

### Data Storage & Persistence
- **Temporary repositories**: Cloned to `temp_repos/` (cleanup is currently commented out)
- **AI context files**: Saved as `ai_context_{pr_number}_{timestamp}.md` for debugging
- **Vector database**: Qdrant storage in `qdrant_storage/` directory
- **Embedding model**: BAAI/bge-small-en-v1.5 loaded on startup

### Multi-Agent Architecture
- **LangGraph State Management**: All agents share `CodeReviewState` TypedDict
- **Agent Status Tracking**: Each agent has status field (PENDING → PROCESSING → COMPLETED/FAILED)
- **Parallel Execution**: Security, code quality, and performance agents run simultaneously
- **Conditional Edges**: Aggregator waits for all 3 agents to complete before proceeding
- **Error Handling**: Failed agents are tracked; system continues with partial results

### Vector Database Collections
Each collection serves a specific purpose:
- `code_graphs`: Stores AST-parsed code structure (functions, classes, relationships)
- `import_files`: Stores source code with import dependencies
- `learnings`: Stores review feedback patterns for continuous improvement

### Currently Python-Only AST Parsing
While tree-sitter libraries are installed for multiple languages, the webhook currently only processes `.py` files for AST analysis (see line 86 in `github_webhook.py`). Other languages will skip AST indexing.