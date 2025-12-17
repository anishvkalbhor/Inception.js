# 🐱 Victor - Enterprise RAG System with LangChain

A production-ready Retrieval-Augmented Generation (RAG) system built with LangChain, featuring intelligent document processing, semantic search, and conversational AI capabilities. The system integrates Google Drive synchronization, web scraping, and multi-modal document processing with enterprise-grade authentication and monitoring.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [RAG Pipeline](#rag-pipeline)
- [Database Schema](#database-schema)
- [Authentication](#authentication)
- [Document Processing](#document-processing)
- [Monitoring & Logging](#monitoring--logging)
- [Development Guide](#development-guide)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)

---

## 🎯 Overview

Victor is an intelligent RAG (Retrieval-Augmented Generation) backend system that combines:

- **Semantic Search**: Vector-based document retrieval using Milvus
- **Conversational AI**: Context-aware question answering with LangChain memory
- **Document Ingestion**: Multi-source document processing (Google Drive, Web Scraping, PDF, DOCX)
- **Authentication**: Secure user management with Better Auth and JWT
- **Real-time Updates**: WebSocket support for live query streaming
- **Enterprise Features**: Conversation management, source citation, and usage analytics

### Use Cases

- 📚 **Knowledge Base Q&A**: Query organizational documents intelligently
- 🎓 **Educational Assistant**: Student-focused AI tutor with document context
- 📄 **Document Search**: Semantic search across large document collections
- 💬 **Conversational AI**: Multi-turn conversations with memory retention

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────┐
│   Next.js 16    │
│   Frontend      │
│  (React 19)     │
└────────┬────────┘
         │ REST API
         │ WebSocket
┌────────▼────────────────────────────────────────┐
│           FastAPI Backend                        │
│  ┌──────────────────────────────────────────┐  │
│  │     LangChain RAG Pipeline               │  │
│  │  ┌────────────┐  ┌─────────────────┐    │  │
│  │  │  Memory    │  │  Vector Store   │    │  │
│  │  │ (MongoDB)  │  │    (Milvus)     │    │  │
│  │  └────────────┘  └─────────────────┘    │  │
│  │  ┌────────────────────────────────────┐ │  │
│  │  │   OpenRouter LLM Integration       │ │  │
│  │  │   (Alibaba Tongyi DeepResearch)    │ │  │
│  │  └────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │     Document Processing Pipeline          │  │
│  │  • PDF Extractor                          │  │
│  │  • DOCX Parser                            │  │
│  │  • Google Drive Sync                      │  │
│  │  • Web Scraper (MoE Website)              │  │
│  │  • Text Chunking & Embeddings            │  │
│  └──────────────────────────────────────────┘  │
└──────────────┬──────────────┬──────────────────┘
               │              │
      ┌────────▼────────┐ ┌──▼──────────┐
      │   MongoDB       │ │   Milvus    │
      │  • Users        │ │  • Vectors  │
      │  • Conversations│ │  • Documents│
      │  • Messages     │ │             │
      │  • Documents    │ └─────────────┘
      └─────────────────┘
```

### Component Interactions

1. **Frontend → Backend**: REST API calls for CRUD operations, WebSocket for streaming
2. **Backend → MongoDB**: User auth, conversation storage, document metadata
3. **Backend → Milvus**: Vector embeddings storage and semantic search
4. **Backend → OpenRouter**: LLM inference for answer generation
5. **Background Jobs**: Document sync, scraping, and indexing tasks

---

## ✨ Features

### Core Features

- ✅ **Conversational RAG**: Multi-turn conversations with context awareness
- ✅ **Semantic Search**: Vector similarity search using sentence transformers
- ✅ **Source Citations**: Automatic document reference with page numbers
- ✅ **Memory Management**: LangChain BaseChatMemory with MongoDB persistence
- ✅ **Streaming Responses**: Real-time answer generation with WebSocket
- ✅ **Multi-format Support**: PDF, DOCX, TXT, Google Docs processing
- ✅ **User Authentication**: JWT-based auth with Better Auth
- ✅ **Conversation Management**: Create, list, delete, and search conversations
- ✅ **Document Ingestion**: Google Drive sync and web scraping
- ✅ **Usage Analytics**: Token tracking and cost monitoring

### Advanced Features

- 🔄 **Automatic Reranking**: Relevance-based document reranking
- 📊 **Embedding Cache**: Redis-based embedding caching (optional)
- 🔍 **Hybrid Search**: Combines keyword and semantic search
- 🎨 **Rich Text Support**: Markdown formatting in responses
- 📈 **Performance Monitoring**: Request timing and error tracking
- 🌐 **CORS Support**: Configurable cross-origin resource sharing

---

## 🛠️ Technology Stack

### Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | FastAPI | 0.109.0+ | High-performance async API |
| RAG Engine | LangChain | 0.1.0+ | RAG orchestration & memory |
| Vector DB | Milvus | 2.4.0+ | Embedding storage & search |
| Database | MongoDB | 4.6.0+ | User data & conversations |
| Embeddings | sentence-transformers | 2.3.0+ | Text to vector conversion |
| LLM Client | httpx | 0.26.0+ | OpenRouter API integration |
| Auth | PyJWT | 2.8.0+ | Token-based authentication |
| Document Processing | PyPDF2, python-docx | Latest | Multi-format parsing |
| Google Integration | google-api-python-client | Latest | Drive synchronization |
| Web Scraping | BeautifulSoup4 | Latest | HTML parsing |

### Frontend Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | Next.js | 16.0.3 | React meta-framework |
| UI Library | React | 19.2.0 | Component-based UI |
| Auth | Better Auth | 1.4.5 | Authentication system |
| Database Client | MongoDB | 7.0.0 | Direct DB access |
| Storage | Supabase | 2.81.1 | File storage (optional) |
| Styling | TailwindCSS | 4.x | Utility-first CSS |
| HTTP Client | Fetch API | Native | API communication |

### Infrastructure

- **Python Environment**: Conda (Python 3.10)
- **Containerization**: Docker & Docker Compose
- **Process Management**: Uvicorn (ASGI server)
- **Development**: Hot reload, automatic API docs

---

## 📋 Prerequisites

### System Requirements

- **OS**: Windows, macOS, or Linux
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 20GB free space (for embeddings and documents)
- **Network**: Stable internet for LLM API calls

### Required Software

```bash
# Core Dependencies
✓ Python 3.10 or higher
✓ Node.js 18.x or higher
✓ Docker & Docker Compose
✓ Git

# Optional Tools
✓ Conda/Miniconda (recommended for Python env)
✓ MongoDB Compass (database GUI)
✓ Postman/Insomnia (API testing)
```

### API Keys & Services

- **OpenRouter API Key**: [Get key](https://openrouter.ai/)
- **MongoDB Instance**: Local or cloud (MongoDB Atlas)
- **Google Drive API**: Service account credentials (for sync)
- **Milvus**: Docker container (included)

---

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/Victor.git
cd Victor
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create conda environment (recommended)
conda create -n VictorVenv python=3.10 -y
conda activate VictorVenv

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, langchain, pymilvus; print('✓ All packages installed')"
```

**Alternative: venv (if not using conda)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install Node.js dependencies
npm install

# Verify installation
npm list next react
```

### 4. Start Milvus Vector Database

```bash
cd ../backend/milvus_store

# Start Milvus with Docker Compose
docker-compose up -d

# Verify Milvus is running
docker ps | grep milvus

# Expected output:
# milvus-standalone    Running
# milvus-minio        Running
# milvus-etcd         Running
```

**Milvus Components:**
- **Standalone**: Main Milvus server (port 19530)
- **MinIO**: Object storage for vector data
- **etcd**: Metadata storage

### 5. MongoDB Setup

**Option A: Local MongoDB**
```bash
# Windows (with MongoDB installed)
net start MongoDB

# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod
```

**Option B: MongoDB Atlas (Cloud)**
1. Create cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Get connection string
3. Update `MONGODB_URI` in `.env`

---

## ⚙️ Configuration

### Backend Environment Variables

Create `backend/.env`:

```env
# ============================================
# MongoDB Configuration
# ============================================
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=victor_rag

# Collections:
# - users: User accounts
# - conversations: Chat sessions
# - messages: Chat history
# - documents: Document metadata
# - embeddings: Cached embeddings (optional)

# ============================================
# Milvus Vector Database
# ============================================
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION=document_embeddings
MILVUS_DIMENSION=768  # sentence-transformers/all-mpnet-base-v2

# ============================================
# OpenRouter LLM Configuration
# ============================================
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
LLM_MODEL=alibaba/tongyi-deepresearch-30b-a3b
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096
SITE_URL=http://localhost:3000
SITE_NAME=VICTOR

# Alternative LLM Models:
# - anthropic/claude-3.5-sonnet
# - openai/gpt-4-turbo
# - meta-llama/llama-3-70b-instruct

# ============================================
# Embeddings Configuration
# ============================================
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
EMBEDDING_DIMENSION=768
EMBEDDING_BATCH_SIZE=32

# ============================================
# RAG Pipeline Settings
# ============================================
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.7

# ============================================
# Authentication
# ============================================
JWT_SECRET=your-secure-jwt-secret-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION=86400  # 24 hours in seconds
REFRESH_TOKEN_EXPIRATION=604800  # 7 days

# ============================================
# Google Drive Sync (Optional)
# ============================================
GOOGLE_CREDENTIALS_PATH=./credentials/google-service-account.json
GOOGLE_DRIVE_FOLDER_ID=your-folder-id
SYNC_INTERVAL=3600  # 1 hour

# ============================================
# Web Scraper Configuration
# ============================================
MOE_BASE_URL=https://www.moe.gov.sa
SCRAPER_USER_AGENT=VictorBot/1.0
SCRAPER_DELAY=2  # Seconds between requests

# ============================================
# Performance & Caching
# ============================================
ENABLE_CACHE=true
CACHE_TTL=3600
MAX_WORKERS=4

# ============================================
# Logging
# ============================================
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Frontend Environment Variables

Create `frontend/.env.local`:

```env
# ============================================
# API Configuration
# ============================================
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# ============================================
# Better Auth Configuration
# ============================================
BETTER_AUTH_SECRET=your-secure-secret-min-32-chars
BETTER_AUTH_URL=http://localhost:3000
MONGODB_URI=mongodb://192.168.0.106:27017

# ============================================
# Supabase (Optional - for file uploads)
# ============================================
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# ============================================
# Feature Flags
# ============================================
NEXT_PUBLIC_ENABLE_STREAMING=true
NEXT_PUBLIC_ENABLE_FILE_UPLOAD=true
NEXT_PUBLIC_MAX_FILE_SIZE=10485760  # 10MB
```

---

## 🎯 Running the Application

### Development Mode

#### 1. Start Milvus (First Time Setup)

```bash
cd backend/milvus_store
docker-compose up -d

# Check status
docker-compose ps
```

#### 2. Start Backend Server

```bash
# Activate conda environment
conda activate VictorVenv

cd backend

# Method 1: Using run_server.py
python run_server.py

# Method 2: Direct uvicorn command
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Method 3: With custom settings
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

**Backend will be available at:**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

#### 3. Start Frontend Development Server

```bash
cd frontend

# Development mode
npm run dev

# Custom port
npm run dev -- -p 3001
```

**Frontend will be available at:**
- App: http://localhost:3000
- Fast Refresh enabled for hot reloading

### Production Mode

#### Backend Production

```bash
# Install production dependencies only
pip install -r requirements.txt

# Or with uvicorn (single worker)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend Production

```bash
cd frontend

# Build for production
npm run build

# Start production server
npm start
```

### Docker Deployment (Coming Soon)

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## 🛠️ Development Guide

### Code Structure Best Practices

```
backend/
├── api/                    # API layer
│   ├── main.py            # App initialization
│   ├── dependencies.py     # Shared dependencies
│   └── routers/           # Endpoint handlers
│       ├── rag.py         # RAG endpoints
│       ├── auth.py        # Auth endpoints
│       ├── conversations.py
│       └── documents.py
├── services/              # Business logic
│   ├── full_langchain_service.py
│   ├── conversation_service.py
│   ├── mongodb_service.py
│   └── embedding_service.py
├── core/                  # Core utilities
│   ├── config.py         # Configuration
│   ├── security.py       # Security utils
│   └── logging_config.py
├── models/               # Pydantic models
│   ├── requests.py
│   └── responses.py
└── scripts/              # Utility scripts
    ├── init_milvus.py
    └── seed_data.py
```

---

**Built with ❤️ using LangChain, FastAPI, and Next.js**
