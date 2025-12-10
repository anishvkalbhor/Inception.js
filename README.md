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
MONGODB_URI=mongodb://192.168.0.106:27017
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
MILVUS_HOST=192.168.0.107
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
pip install -r requirements-prod.txt

# Run with production settings
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

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

# Or use PM2 for process management
pm2 start npm --name "Victor-frontend" -- start
```

### Docker Deployment (Coming Soon)

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## 📡 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}

Response: 201 Created
{
  "user_id": "user_123abc",
  "email": "user@example.com",
  "token": "eyJhbGc..."
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### RAG Endpoints

#### Ask Question (Streaming)
```http
POST /api/ask
Authorization: Bearer {token}
Content-Type: application/json

{
  "query": "What are the admission requirements?",
  "conversation_id": "conv_123",
  "user_id": "user_123",
  "stream": true,
  "top_k": 5
}

Response: 200 OK (Server-Sent Events)
data: {"type": "token", "content": "Based"}
data: {"type": "token", "content": " on"}
data: {"type": "source", "content": {"title": "Admission Guide", "page": 5}}
data: {"type": "done"}
```

#### Ask Question (Non-Streaming)
```http
POST /api/ask
Authorization: Bearer {token}
Content-Type: application/json

{
  "query": "What are the admission requirements?",
  "conversation_id": "conv_123",
  "user_id": "user_123",
  "stream": false
}

Response: 200 OK
{
  "answer": "The admission requirements include...",
  "sources": [
    {
      "title": "Admission Guide 2024",
      "page": 5,
      "relevance_score": 0.92,
      "content_preview": "To be admitted..."
    }
  ],
  "conversation_id": "conv_123",
  "message_id": "msg_456",
  "tokens_used": 245,
  "processing_time_ms": 1250
}
```

### Conversation Management

#### Create Conversation
```http
POST /api/conversations
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Admission Questions",
  "user_id": "user_123",
  "metadata": {
    "category": "admissions"
  }
}

Response: 201 Created
{
  "conversation_id": "conv_789",
  "title": "Admission Questions",
  "created_at": "2024-12-09T10:30:00Z",
  "message_count": 0
}
```

#### List Conversations
```http
GET /api/conversations/{user_id}?limit=20&skip=0
Authorization: Bearer {token}

Response: 200 OK
{
  "conversations": [
    {
      "conversation_id": "conv_789",
      "title": "Admission Questions",
      "created_at": "2024-12-09T10:30:00Z",
      "updated_at": "2024-12-09T11:45:00Z",
      "message_count": 8,
      "last_message": "What are the deadlines?"
    }
  ],
  "total": 15,
  "limit": 20,
  "skip": 0
}
```

#### Get Conversation Messages
```http
GET /api/conversations/{conversation_id}/messages?limit=50
Authorization: Bearer {token}

Response: 200 OK
{
  "messages": [
    {
      "message_id": "msg_001",
      "role": "user",
      "content": "What are the admission requirements?",
      "timestamp": "2024-12-09T10:31:00Z"
    },
    {
      "message_id": "msg_002",
      "role": "assistant",
      "content": "The admission requirements include...",
      "sources": [...],
      "timestamp": "2024-12-09T10:31:05Z"
    }
  ],
  "total": 8,
  "conversation_id": "conv_789"
}
```

#### Delete Conversation
```http
DELETE /api/conversations/{conversation_id}
Authorization: Bearer {token}

Response: 204 No Content
```

### Document Management

#### Trigger Google Drive Sync
```http
POST /api/sync/trigger
Authorization: Bearer {token}
Content-Type: application/json

{
  "folder_id": "google-drive-folder-id",
  "force": false
}

Response: 202 Accepted
{
  "job_id": "sync_job_123",
  "status": "started",
  "estimated_duration": "5-10 minutes"
}
```

#### Check Sync Status
```http
GET /api/sync/status/{job_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "job_id": "sync_job_123",
  "status": "processing",
  "progress": 65,
  "documents_processed": 13,
  "documents_total": 20,
  "errors": []
}
```

#### Trigger Web Scraper
```http
POST /api/scraper/run
Authorization: Bearer {token}
Content-Type: application/json

{
  "target_url": "https://www.moe.gov.sa",
  "max_depth": 3,
  "filters": ["admissions", "programs"]
}

Response: 202 Accepted
{
  "job_id": "scrape_job_456",
  "status": "started"
}
```

#### List Documents
```http
GET /api/documents?limit=20&skip=0&filter=pdf
Authorization: Bearer {token}

Response: 200 OK
{
  "documents": [
    {
      "document_id": "doc_123",
      "title": "Student Handbook 2024.pdf",
      "file_type": "pdf",
      "page_count": 45,
      "indexed_at": "2024-12-09T08:00:00Z",
      "chunk_count": 90,
      "size_bytes": 2048576
    }
  ],
  "total": 156
}
```

### Health & Monitoring

#### Health Check
```http
GET /health

Response: 200 OK
{
  "status": "healthy",
  "components": {
    "mongodb": "connected",
    "milvus": "connected",
    "openrouter": "accessible"
  },
  "version": "1.0.0",
  "uptime_seconds": 3600
}
```

#### System Stats
```http
GET /api/stats
Authorization: Bearer {token}

Response: 200 OK
{
  "total_documents": 156,
  "total_conversations": 1247,
  "total_messages": 8932,
  "active_users": 45,
  "vector_count": 14040,
  "avg_response_time_ms": 1250,
  "tokens_used_today": 125000
}
```

---

## 🧠 RAG Pipeline

### Architecture Overview

The RAG pipeline consists of three main stages:

1. **Retrieval**: Semantic search in Milvus
2. **Augmentation**: Context preparation with memory
3. **Generation**: LLM response with sources

### Detailed Pipeline Flow

```python
# 1. Query Processing
User Query → Embedding Generation → Vector Search

# 2. Context Retrieval
Vector Search Results → Document Reranking → Top K Selection

# 3. Memory Integration
Conversation History → Context Window → Prompt Construction

# 4. LLM Generation
Augmented Prompt → OpenRouter API → Streamed Response

# 5. Source Citation
Retrieved Documents → Metadata Extraction → Citation Formatting
```

### LangChain Components

#### Memory Management

```python
from langchain.memory.chat_memory import BaseChatMemory
from services.mongodb_service import MongoDBService

class MongoDBChatMemory(BaseChatMemory):
    """
    Custom LangChain memory backed by MongoDB
    
    Features:
    - Persistent conversation history
    - Automatic message pruning
    - Context window management
    - Multi-user isolation
    """
    
    def __init__(self, conversation_id: str, user_id: str):
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.db = MongoDBService()
    
    def save_context(self, inputs, outputs):
        """Save conversation turn to MongoDB"""
        self.db.add_message(
            conversation_id=self.conversation_id,
            role="user",
            content=inputs["input"]
        )
        self.db.add_message(
            conversation_id=self.conversation_id,
            role="assistant",
            content=outputs["output"]
        )
    
    def load_memory_variables(self, inputs):
        """Load conversation history from MongoDB"""
        messages = self.db.get_conversation_messages(
            conversation_id=self.conversation_id,
            limit=10  # Last 10 messages
        )
        return {"history": messages}
```

#### Vector Store Integration

```python
from pymilvus import Collection, connections
from langchain.vectorstores import Milvus

class MilvusVectorStore:
    """
    Milvus vector store wrapper for LangChain
    
    Features:
    - Automatic connection management
    - Batch embedding insertion
    - Similarity search with filtering
    - Metadata support
    """
    
    def __init__(self, host, port, collection_name):
        connections.connect(host=host, port=port)
        self.collection = Collection(collection_name)
        self.collection.load()
    
    def similarity_search(self, query_vector, top_k=5, filter_expr=None):
        """
        Perform similarity search
        
        Args:
            query_vector: Embedding vector
            top_k: Number of results
            filter_expr: Milvus filter expression
        
        Returns:
            List of (document, score) tuples
        """
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        
        results = self.collection.search(
            data=[query_vector],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=filter_expr,
            output_fields=["text", "metadata", "doc_id"]
        )
        
        return [
            (hit.entity.get("text"), hit.distance, hit.entity.get("metadata"))
            for hit in results[0]
        ]
```

#### RAG Chain Construction

```python
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

# Custom prompt template
PROMPT_TEMPLATE = """
You are VICTOR, an AI assistant with access to a knowledge base.

Context from documents:
{context}

Conversation history:
{chat_history}

User question: {question}

Instructions:
1. Answer based on the provided context
2. If information is not in context, say so
3. Cite sources with [Source: document_name, Page: X]
4. Be concise and accurate

Answer:
"""

prompt = PromptTemplate(
    template=PROMPT_TEMPLATE,
    input_variables=["context", "chat_history", "question"]
)

# Build RAG chain
rag_chain = ConversationalRetrievalChain.from_llm(
    llm=openrouter_llm,
    retriever=milvus_retriever,
    memory=mongodb_memory,
    combine_docs_chain_kwargs={"prompt": prompt},
    return_source_documents=True
)
```

### Embedding Generation

```python
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    """
    Generate embeddings for text using sentence-transformers
    
    Model: all-mpnet-base-v2 (768 dimensions)
    Performance: ~2000 embeddings/second on GPU
    """
    
    def __init__(self, model_name="sentence-transformers/all-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, texts: list) -> list:
        """Batch embed multiple documents"""
        return self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        ).tolist()
    
    def embed_query(self, text: str) -> list:
        """Embed single query"""
        return self.model.encode(text).tolist()
```

### Document Chunking Strategy

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_document(text: str, chunk_size=500, chunk_overlap=50):
    """
    Split document into semantic chunks
    
    Strategy:
    1. Split by paragraphs first
    2. Then by sentences
    3. Finally by characters if needed
    
    Args:
        text: Document text
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks
    
    Returns:
        List of text chunks with metadata
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len
    )
    
    chunks = splitter.split_text(text)
    
    # Add metadata
    return [
        {
            "text": chunk,
            "chunk_index": i,
            "chunk_size": len(chunk),
            "overlap_start": chunk_overlap if i > 0 else 0
        }
        for i, chunk in enumerate(chunks)
    ]
```

---

## 🗄️ Database Schema

### MongoDB Collections

#### 1. Users Collection
```javascript
{
  "_id": ObjectId("..."),
  "user_id": "user_123abc",
  "email": "user@example.com",
  "password_hash": "$2b$12$...",  // bcrypt hash
  "name": "John Doe",
  "role": "student",  // student, admin
  "created_at": ISODate("2024-12-09T10:00:00Z"),
  "last_login": ISODate("2024-12-09T15:30:00Z"),
  "preferences": {
    "theme": "dark",
    "language": "en"
  },
  "usage_stats": {
    "total_queries": 145,
    "total_tokens": 25000
  }
}

// Indexes
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "user_id": 1 }, { unique: true })
```

#### 2. Conversations Collection
```javascript
{
  "_id": ObjectId("..."),
  "conversation_id": "conv_789xyz",
  "user_id": "user_123abc",
  "title": "Admission Questions",
  "created_at": ISODate("2024-12-09T10:30:00Z"),
  "updated_at": ISODate("2024-12-09T11:45:00Z"),
  "message_count": 8,
  "metadata": {
    "category": "admissions",
    "tags": ["undergraduate", "requirements"],
    "language": "en"
  },
  "summary": "Discussion about admission requirements...",
  "status": "active"  // active, archived, deleted
}

// Indexes
db.conversations.createIndex({ "conversation_id": 1 }, { unique: true })
db.conversations.createIndex({ "user_id": 1, "created_at": -1 })
db.conversations.createIndex({ "user_id": 1, "status": 1 })
```

#### 3. Messages Collection
```javascript
{
  "_id": ObjectId("..."),
  "message_id": "msg_456def",
  "conversation_id": "conv_789xyz",
  "role": "assistant",  // user, assistant
  "content": "The admission requirements include...",
  "timestamp": ISODate("2024-12-09T10:31:05Z"),
  "sources": [
    {
      "document_id": "doc_123",
      "title": "Admission Guide 2024.pdf",
      "page": 5,
      "relevance_score": 0.92,
      "text_snippet": "To be admitted, students must..."
    }
  ],
  "metadata": {
    "tokens_used": 245,
    "processing_time_ms": 1250,
    "model": "alibaba/tongyi-deepresearch-30b-a3b",
    "top_k": 5
  }
}

// Indexes
db.messages.createIndex({ "conversation_id": 1, "timestamp": 1 })
db.messages.createIndex({ "message_id": 1 }, { unique: true })
```

#### 4. Documents Collection
```javascript
{
  "_id": ObjectId("..."),
  "document_id": "doc_123",
  "title": "Student Handbook 2024.pdf",
  "file_path": "/storage/documents/handbook_2024.pdf",
  "file_type": "pdf",
  "source": "google_drive",  // google_drive, scraper, upload
  "source_id": "1abc-google-drive-file-id",
  "uploaded_by": "user_123abc",
  "uploaded_at": ISODate("2024-12-09T08:00:00Z"),
  "processed_at": ISODate("2024-12-09T08:05:00Z"),
  "metadata": {
    "page_count": 45,
    "size_bytes": 2048576,
    "language": "en",
    "author": "University Administration",
    "category": "handbook"
  },
  "processing_status": "completed",  // pending, processing, completed, failed
  "chunk_count": 90,
  "milvus_ids": [1, 2, 3, ...],  // Vector IDs in Milvus
  "checksum": "sha256:abc123..."
}

// Indexes
db.documents.createIndex({ "document_id": 1 }, { unique: true })
db.documents.createIndex({ "source": 1, "source_id": 1 })
db.documents.createIndex({ "processing_status": 1 })
db.documents.createIndex({ "uploaded_at": -1 })
```

#### 5. Sync Jobs Collection
```javascript
{
  "_id": ObjectId("..."),
  "job_id": "sync_job_123",
  "job_type": "google_drive_sync",  // google_drive_sync, web_scrape
  "status": "processing",  // started, processing, completed, failed
  "started_at": ISODate("2024-12-09T09:00:00Z"),
  "completed_at": null,
  "progress": {
    "current": 13,
    "total": 20,
    "percentage": 65
  },
  "config": {
    "folder_id": "google-drive-folder-id",
    "force_update": false
  },
  "results": {
    "documents_processed": 13,
    "documents_added": 8,
    "documents_updated": 5,
    "errors": []
  },
  "error_message": null
}

// Indexes
db.sync_jobs.createIndex({ "job_id": 1 }, { unique: true })
db.sync_jobs.createIndex({ "status": 1, "started_at": -1 })
```

### Milvus Collections

#### Document Embeddings Collection
```python
# Collection Schema
schema = {
    "collection_name": "document_embeddings",
    "description": "Document chunk embeddings for semantic search",
    "fields": [
        {
            "name": "id",
            "type": "INT64",
            "is_primary": True,
            "auto_id": True
        },
        {
            "name": "embedding",
            "type": "FLOAT_VECTOR",
            "dim": 768,  # all-mpnet-base-v2 dimension
            "description": "Text embedding vector"
        },
        {
            "name": "document_id",
            "type": "VARCHAR",
            "max_length": 100,
            "description": "Reference to MongoDB document"
        },
        {
            "name": "chunk_index",
            "type": "INT64",
            "description": "Chunk position in document"
        },
        {
            "name": "text",
            "type": "VARCHAR",
            "max_length": 2000,
            "description": "Original text content"
        },
        {
            "name": "page_number",
            "type": "INT64",
            "description": "Page number (for PDFs)"
        },
        {
            "name": "metadata",
            "type": "JSON",
            "description": "Additional metadata"
        }
    ]
}

# Index Configuration
index_params = {
    "metric_type": "L2",  # Euclidean distance
    "index_type": "IVF_FLAT",  # Inverted File Index
    "params": {"nlist": 1024}
}

# Search Parameters
search_params = {
    "metric_type": "L2",
    "params": {"nprobe": 10}  # Number of clusters to search
}
```

---

## 🔐 Authentication

### Better Auth Configuration

Better Auth provides secure authentication with MongoDB adapter.

#### Backend Integration

```python
# services/auth_service.py
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET")
        self.algorithm = "HS256"
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user_id: str, expires_delta: timedelta = None):
        """Generate JWT access token"""
        if expires_delta is None:
            expires_delta = timedelta(hours=24)
        
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str):
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
```

#### Frontend Integration

```typescript
// lib/auth.ts
import { BetterAuth } from "better-auth/client";

export const authClient = BetterAuth({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  storage: {
    type: "cookie",
    name: "Victor-session"
  }
});

// Login function
export async function login(email: string, password: string) {
  const response = await authClient.signIn.email({
    email,
    password
  });
  
  if (response.error) {
    throw new Error(response.error.message);
  }
  
  return response.data;
}

// Get current user
export async function getCurrentUser() {
  const session = await authClient.getSession();
  return session?.user;
}

// Logout function
export async function logout() {
  await authClient.signOut();
}
```

#### Protected Routes

```python
# api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    auth_service = AuthService()
    
    user_id = auth_service.verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # Fetch user from database
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# Usage in routes
@app.post("/api/ask")
async def ask_question(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    # User is authenticated
    pass
```

---

## 📄 Document Processing

### PDF Processing

```python
import PyPDF2
from typing import List, Dict

class PDFProcessor:
    """Extract text and metadata from PDF files"""
    
    def process_pdf(self, file_path: str) -> Dict:
        """
        Extract text from PDF with page tracking
        
        Returns:
            {
                "text": str,
                "page_count": int,
                "pages": List[{"page_num": int, "text": str}],
                "metadata": dict
            }
        """
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            pages = []
            full_text = []
            
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                page_text = page.extract_text()
                pages.append({
                    "page_num": page_num,
                    "text": page_text
                })
                full_text.append(page_text)
            
            metadata = {
                "title": pdf_reader.metadata.get("/Title", ""),
                "author": pdf_reader.metadata.get("/Author", ""),
                "subject": pdf_reader.metadata.get("/Subject", ""),
                "creator": pdf_reader.metadata.get("/Creator", ""),
                "producer": pdf_reader.metadata.get("/Producer", ""),
                "creation_date": pdf_reader.metadata.get("/CreationDate", "")
            }
            
            return {
                "text": "\n\n".join(full_text),
                "page_count": len(pages),
                "pages": pages,
                "metadata": metadata
            }
```

### DOCX Processing

```python
from docx import Document

class DOCXProcessor:
    """Extract text from DOCX files"""
    
    def process_docx(self, file_path: str) -> Dict:
        """
        Extract text from DOCX with paragraph tracking
        
        Returns:
            {
                "text": str,
                "paragraphs": List[str],
                "metadata": dict
            }
        """
        doc = Document(file_path)
        
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        
        # Extract core properties
        core_props = doc.core_properties
        metadata = {
            "title": core_props.title,
            "author": core_props.author,
            "subject": core_props.subject,
            "keywords": core_props.keywords,
            "created": core_props.created,
            "modified": core_props.modified
        }
        
        return {
            "text": "\n\n".join(paragraphs),
            "paragraphs": paragraphs,
            "metadata": metadata
        }
```

### Google Drive Sync

```python
from googleapiclient.discovery import build
from google.oauth2 import service_account

class GoogleDriveSync:
    """Sync documents from Google Drive"""
    
    def __init__(self, credentials_path: str):
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        self.service = build('drive', 'v3', credentials=credentials)
    
    def sync_folder(self, folder_id: str) -> List[Dict]:
        """
        Sync all documents from a Google Drive folder
        
        Process:
        1. List all files in folder
        2. Download new/updated files
        3. Process and index documents
        4. Update MongoDB metadata
        """
        # List files
        query = f"'{folder_id}' in parents and trashed=false"
        results = self.service.files().list(
            q=query,
            fields="files(id, name, mimeType, modifiedTime, size)"
        ).execute()
        
        files = results.get('files', [])
        synced_documents = []
        
        for file in files:
            # Check if already synced
            existing_doc = db.get_document_by_source_id(file['id'])
            
            if existing_doc and existing_doc['modified_time'] >= file['modifiedTime']:
                continue  # Skip unchanged files
            
            # Download and process
            content = self.download_file(file['id'])
            processed = self.process_file(content, file)
            
            # Index in Milvus
            embeddings = embedding_service.embed_documents(processed['chunks'])
            milvus_ids = milvus_client.insert_vectors(embeddings, processed['metadata'])
            
            # Save to MongoDB
            doc_id = db.save_document({
                "title": file['name'],
                "source": "google_drive",
                "source_id": file['id'],
                "modified_time": file['modifiedTime'],
                "milvus_ids": milvus_ids,
                **processed
            })
            
            synced_documents.append(doc_id)
        
        return synced_documents
```

### Web Scraper

```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

class WebScraper:
    """Scrape and index web content"""
    
    def __init__(self, base_url: str, delay: float = 2.0):
        self.base_url = base_url
        self.delay = delay
        self.visited = set()
    
    def scrape_recursive(self, url: str, max_depth: int = 3, current_depth: int = 0):
        """
        Recursively scrape website
        
        Features:
        - Respect robots.txt
        - Rate limiting
        - Content extraction
        - Link following
        """
        if current_depth > max_depth or url in self.visited:
            return []
        
        self.visited.add(url)
        time.sleep(self.delay)  # Rate limiting
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract content
        content = self.extract_content(soup)
        
        # Save document
        doc_id = db.save_document({
            "title": soup.title.string if soup.title else url,
            "source": "scraper",
            "source_id": url,
            "content": content,
            "scraped_at": datetime.utcnow()
        })
        
        # Process and index
        chunks = chunk_document(content)
        embeddings = embedding_service.embed_documents([c['text'] for c in chunks])
        milvus_client.insert_vectors(embeddings, {"doc_id": doc_id})
        
        # Follow links
        documents = [doc_id]
        if current_depth < max_depth:
            links = soup.find_all('a', href=True)
            for link in links:
                next_url = urljoin(url, link['href'])
                if self.is_same_domain(next_url):
                    documents.extend(self.scrape_recursive(next_url, max_depth, current_depth + 1))
        
        return documents
    
    def extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML"""
        # Remove unwanted tags
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        # Extract text from main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        return main_content.get_text(separator='\n', strip=True) if main_content else ""
    
    def is_same_domain(self, url: str) -> bool:
        """Check if URL is from same domain"""
        return urlparse(url).netloc == urlparse(self.base_url).netloc
```

---

## 📊 Monitoring & Logging

### Logging Configuration

```python
# core/logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured JSON logging"""
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger

# Usage
logger = setup_logging()
logger.info("Application started", extra={"component": "main"})
```

### Request Logging Middleware

```python
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    logger.info(
        "HTTP Request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time_ms": round(process_time * 1000, 2),
            "client_ip": request.client.host
        }
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Error Tracking

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch and log all unhandled exceptions"""
    logger.error(
        "Unhandled exception",
        extra={
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
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

### Adding New Endpoints

```python
# api/routers/example.py
from fastapi import APIRouter, Depends
from models.requests import ExampleRequest
from models.responses import ExampleResponse
from api.dependencies import get_current_user

router = APIRouter(prefix="/api/example", tags=["example"])

@router.post("/", response_model=ExampleResponse)
async def create_example(
    request: ExampleRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create new example
    
    - **name**: Example name
    - **description**: Optional description
    """
    # Implementation
    pass

# Register in main.py
from api.routers import example
app.include_router(example.router)
```

### Testing

```python
# tests/test_rag.py
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_ask_question():
    """Test RAG question endpoint"""
    response = client.post(
        "/api/ask",
        json={
            "query": "What is the admission process?",
            "conversation_id": "test_conv",
            "user_id": "test_user"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code == 200
    assert "answer" in response.json()
    assert "sources" in response.json()

# Run tests
pytest tests/ -v
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. LangChain Import Errors

**Problem**: `ModuleNotFoundError: No module named 'langchain_core.memory'`

**Solution**:
```bash
# Verify conda environment
conda activate VictorVenv
python -c "import langchain; print(langchain.__version__)"

# Should show 0.1.0
# If not, reinstall
pip uninstall langchain langchain-core -y
pip install langchain==0.1.0 langchain-core==0.1.23
```

#### 2. Milvus Connection Failed

**Problem**: `Cannot connect to Milvus server`

**Solution**:
```bash
# Check Milvus is running
docker ps | grep milvus

# If not running, start it
cd backend/milvus_store
docker-compose up -d

# Check logs
docker-compose logs -f milvus-standalone

# Verify connection
python -c "from pymilvus import connections; connections.connect(host='192.168.0.107', port='19530')"
```

#### 3. MongoDB Authentication Error

**Problem**: `Authentication failed`

**Solution**:
```bash
# Check MongoDB is accessible
mongosh mongodb://192.168.0.106:27017

# If using auth, update .env
MONGODB_URI=mongodb://username:password@192.168.0.106:27017/victor_rag?authSource=admin
```

#### 4. OpenRouter API Errors

**Problem**: `401 Unauthorized` or rate limit errors

**Solution**:
```bash
# Verify API key
curl https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"

# Check usage limits
# Update LLM_MODEL if needed in .env
```

#### 5. Embedding Generation Slow

**Problem**: Embeddings taking too long

**Solution**:
```python
# Enable GPU acceleration (if available)
pip install sentence-transformers[gpu]

# Or reduce batch size in .env
EMBEDDING_BATCH_SIZE=16  # Down from 32

# Consider caching embeddings in MongoDB
```

---

## ⚡ Performance Optimization

### Backend Optimization

1. **Enable Async Operations**
```python
# Use async MongoDB operations
async def get_conversations(user_id: str):
    async with await motor_client.start_session() as session:
        cursor = db.conversations.find({"user_id": user_id})
        return await cursor.to_list(length=100)
```

2. **Implement Connection Pooling**
```python
# MongoDB connection pool
client = MongoClient(
    MONGODB_URI,
    maxPoolSize=50,
    minPoolSize=10
)
```

3. **Cache Embeddings**
```python
# Redis cache for embeddings
from redis import Redis

cache = Redis(host='localhost', port=6379)

def get_embedding(text: str):
    cached = cache.get(f"emb:{hash(text)}")
    if cached:
        return json.loads(cached)
    
    embedding = model.encode(text)
    cache.setex(f"emb:{hash(text)}", 3600, json.dumps(embedding))
    return embedding
```

### Milvus Optimization

```python
# Optimize index parameters
index_params = {
    "metric_type": "L2",
    "index_type": "IVF_PQ",  # Product Quantization for compression
    "params": {
        "nlist": 2048,  # More clusters for better accuracy
        "m": 8,         # Number of subquantizers
        "nbits": 8      # Bits per subvector
    }
}

# Optimize search parameters
search_params = {
    "metric_type": "L2",
    "params": {
        "nprobe": 32  # More clusters searched = higher accuracy
    }
}
```

### Frontend Optimization

```typescript
// Implement virtual scrolling for conversations
import { VirtualScroller } from '@tanstack/react-virtual'

// Lazy load components
const ChatInterface = lazy(() => import('./components/ChatInterface'))

// Debounce search
import { debounce } from 'lodash'
const debouncedSearch = debounce(searchConversations, 300)
```

---

## 📄 License

This is a private academic project for Semester 7.

**Confidential** - Not for public distribution.

---

## 👥 Contributors

- **Project Lead**: [Your Name]
- **Advisor**: [Advisor Name]
- **Institution**: [University Name]

---

## 📞 Support

For issues or questions:
- 📧 Email: [your-email]
- 💬 Discord: [discord-server]
- 📝 Issues: [GitHub Issues](https://github.com/yourusername/Victor/issues)

---

## 🗺️ Roadmap

### Version 1.1 (Planned)
- [ ] Multi-language support (Arabic, English)
- [ ] Voice input/output
- [ ] Image document processing (OCR)
- [ ] Advanced analytics dashboard
- [ ] Export conversations to PDF
- [ ] Mobile app (React Native)

### Version 2.0 (Future)
- [ ] Multi-tenant support
- [ ] Fine-tuned domain-specific LLM
- [ ] Real-time collaboration
- [ ] Integration with Learning Management Systems
- [ ] Advanced RAG techniques (HyDE, RAG-Fusion)

---

**Built with ❤️ using LangChain, FastAPI, and Next.js**