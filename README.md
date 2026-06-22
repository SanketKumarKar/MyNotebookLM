# 📚 MyNotebookLM

**AI-Powered Personalized Learning System** — Knowledge Graph · Adaptive Memory · Intelligent Tutoring

## What It Does

Upload your study materials (PDFs, presentations, images of handwritten notes, text files) and MyNotebookLM will:

- **Parse & understand** all uploaded content using direct parsers (pypdf, python-pptx, pytesseract OCR)
- **Build a knowledge graph** of concepts and relationships in Neo4j
- **Store dense vector embeddings** in Qdrant for semantic retrieval
- **Remember your learning history** via Mem0 cloud API — tracks weaknesses, preferences, progress
- **Orchestrate everything** via a LangGraph multi-agent pipeline
- **Serve a Streamlit frontend** with chat, quiz, source citations, and revision scheduling

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     HOST MACHINE                        │
│                                                         │
│   Ollama (local) OR Mistral Cloud API                   │
│   ├── mistral (local) or API → LLM for reasoning        │
│   └── qwen3-embedding:4b   → Embeddings (2560-dim)      │
│                                                         │
│   Accessible at: http://host.docker.internal:11434      │
└─────────────────────────────────────────────────────────┘
           ▲ http calls from Docker containers
           │
┌─────────────────────────────────────────────────────────┐
│              DOCKER NETWORK: mynotebooklm_net           │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │  Qdrant  │  │  Neo4j   │  │  MyNotebookLM App    │  │
│  │ :6333    │  │ :7474    │  │  Streamlit :8501      │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Docker Desktop** installed and running
2. **Ollama** installed on your host machine with models pulled:
   ```bash
   ollama pull mistral
   ollama pull qwen3-embedding:4b
   ```
3. **Mem0 API key** from [app.mem0.ai](https://app.mem0.ai)
4. *(Optional)* **Mistral API key**. If provided in `.env`, the cloud API takes priority over local Ollama for the chat model.

## Quick Start

1. **Clone and configure:**
   ```bash
   cd MyNotebookLM
   cp .env.example .env
   # Edit .env and set your MEM0_API_KEY
   ```

2. **Start Ollama** (if not already running):
   ```bash
   ollama serve
   ```

3. **Launch with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **Open the app:** [http://localhost:8501](http://localhost:8501)

## Features

| Page | Description |
|------|-------------|
| 💬 **Chat** | Conversational AI tutor with citations and personalized responses |
| 📤 **Upload** | Multi-file ingestion with progress tracking and stats |
| 📝 **Quiz** | AI-generated MCQ and short-answer quizzes with grading |
| 🧠 **Profile** | Learning memory viewer, strengths, and weak areas |
| 📅 **Revision** | Spaced repetition schedule with CSV export |

## Tech Stack

- **LLM:** Mistral Cloud API (if MISTRAL_API_KEY is set) OR mistral via local Ollama
- **Embeddings:** qwen3-embedding:4b via Ollama (2560-dim)
- **Vector DB:** Qdrant
- **Graph DB:** Neo4j
- **Memory:** Mem0 Cloud API
- **Orchestration:** LangGraph (multi-agent pipeline)
- **Retrieval:** Hybrid (Vector + BM25 + Graph) with BGE cross-encoder reranking
- **Frontend:** Streamlit
- **Document Parsing:** pypdf, python-pptx, pytesseract+Pillow

## Project Structure

```
MyNotebookLM/
├── app.py                    # Streamlit entry point
├── config/settings.py        # Pydantic BaseSettings
├── ingestion/                # Parse → Chunk → Extract → Graph → Vectorize
├── retrieval/                # Vector + BM25 + Graph → RRF fusion → Rerank
├── memory/                   # Mem0 cloud API wrapper
├── agents/                   # LangGraph nodes + workflow
├── personalization/          # Quiz engine, weakness tracking, revision scheduling
├── ui/                       # Streamlit pages and components
├── utils/                    # Logger, helpers, LLM singletons
├── docker-compose.yml        # Qdrant + Neo4j + App
└── Dockerfile
```

## License

MIT
