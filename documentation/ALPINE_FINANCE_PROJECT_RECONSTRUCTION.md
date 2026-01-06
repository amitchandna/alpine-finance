# Alpine Finance: Complete Project Reconstruction

## Project Overview

**Alpine Finance** is a production-ready RAG (Retrieval Augmented Generation) system for analyzing SEC 10-K financial filings using LLMs and vector search. The system enables semantic search and Q&A across 67,440 records spanning 12,000+ tickers.

### Key Features
- **Semantic Search**: Query financial documents using natural language
- **Multi-embedding Support**: Small (384d), Medium (768d), and Large (1024d) embeddings
- **Local LLM Integration**: Ollama-based answer generation (CPU-friendly)
- **Production FastAPI Backend**: RESTful API with health checks and statistics
- **Django ORM**: PostgreSQL + pgvector for data management
- **Configurable Models**: Hot-swappable embedding and LLM models

### Tech Stack
- **Backend**: Python, Django, FastAPI
- **Database**: PostgreSQL with pgvector extension
- **Vector Search**: pgvector (native PostgreSQL)
- **Embeddings**: sentence-transformers (multiple models)
- **LLM**: Ollama (tinyllama, qwen, phi3)
- **Deployment**: Docker Compose
- **API**: FastAPI with Uvicorn

---

## Architecture

### High-Level Flow

```
User Query
    ↓
FastAPI Endpoint (/ask)
    ↓
[1] Generate Query Embedding (sentence-transformers)
    ↓
[2] Vector Search (pgvector with filters)
    - Filter by: ticker, year, section
    - Returns: Top-K most similar chunks
    ↓
[3] Context Enrichment (PostgreSQL)
    - Retrieve full metadata
    - Company info, filing dates, sections
    ↓
[4] LLM Answer Generation (Ollama)
    - Combine chunks into context
    - Generate answer with citations
    ↓
[5] Return Response
    - Answer text
    - Source citations
    - Metadata (cost, tokens, similarity)
```

### Data Architecture

```
TenKData (raw_ten_k_data)
  - Original 10-K filings
  - All sections as separate columns
  ↓
RAGFilingSection (3 tables: Small/Medium/Large)
  - Extracted sections with metadata
  - ticker, filing_date, section_name, full_text
  ↓
RAGChunk (3 tables: Small/Medium/Large)
  - Text chunks with embeddings
  - Optimized sizes per embedding model:
    * Small (384d): 200 tokens, 30 overlap
    * Medium (768d): 300 tokens, 50 overlap
    * Large (1024d): 450 tokens, 70 overlap
```

---

## Database Schema

### Core Tables

#### RAGFilingSectionSmall / Medium / Large
```sql
CREATE TABLE rag_filing_sections_small (
    id SERIAL PRIMARY KEY,
    filing_type TEXT,           -- e.g., "10-K"
    ticker TEXT,                -- e.g., "AAPL"
    filing_date DATE,
    filing_url TEXT,
    source_table TEXT,          -- "raw_ten_k_data"
    source_column TEXT,         -- e.g., "section_one_a"
    section_name TEXT,          -- e.g., "Item 1A - Risk Factors"
    full_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sections_ticker_type_section 
    ON rag_filing_sections_small(ticker, filing_type, section_name);
```

#### RAGChunkSmall / Medium / Large
```sql
CREATE TABLE rag_chunks_small (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES rag_filing_sections_small(id),
    chunk_index INTEGER,
    text TEXT,
    token_count INTEGER,
    embedding_384 vector(384),  -- pgvector type
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chunks_section 
    ON rag_chunks_small(section_id, chunk_index);

CREATE INDEX idx_chunks_embedding_cosine 
    ON rag_chunks_small USING ivfflat (embedding_384 vector_cosine_ops)
    WITH (lists = 100);
```

### Supported Embedding Models

| Size | Dimensions | Model | Chunk Size | Overlap |
|------|-----------|-------|------------|---------|
| Small | 384 | BAAI/bge-small-en-v1.5 | 200 tokens | 30 |
| Medium | 768 | BAAI/bge-base-en-v1.5 | 300 tokens | 50 |
| Large | 1024 | BAAI/bge-large-en-v1.5 | 450 tokens | 70 |

---

## Project Structure

```
alpine-finance/
├── django_project/
│   ├── django_project/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── upper_lake/           # Main Django app
│   │   ├── models.py          # RAGFilingSection, RAGChunk models
│   │   ├── api/
│   │   │   └── main.py        # FastAPI application
│   │   ├── services/
│   │   │   ├── vector_search.py    # pgvector search service
│   │   │   ├── qa_service.py       # RAG Q&A orchestration
│   │   │   └── embedding_service.py # Embedding generation
│   │   ├── management/commands/
│   │   │   ├── chunk_filings.py    # Chunking command
│   │   │   ├── generate_embeddings.py # Embedding generation
│   │   │   └── chat.py             # CLI chat interface
│   │   └── chunking/
│   │       ├── service.py          # Chunking logic
│   │       └── utils.py            # Text cleaning utilities
│   ├── manage.py
│   └── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## Core Components

### 1. Django Models

```python
# upper_lake/models.py

from django.db import models
from pgvector.django import VectorField

class RAGFilingSectionSmall(models.Model):
    """Small embeddings (384-dim) - fastest"""
    id = models.AutoField(primary_key=True)
    filing_type = models.TextField()
    ticker = models.TextField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    source_table = models.TextField()
    source_column = models.TextField()
    section_name = models.TextField()
    full_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rag_filing_sections_small"
        indexes = [
            models.Index(fields=["ticker", "filing_type", "section_name"]),
        ]

class RAGChunkSmall(models.Model):
    """Chunks for 384-dim embeddings"""
    id = models.AutoField(primary_key=True)
    section = models.ForeignKey(
        RAGFilingSectionSmall, 
        on_delete=models.CASCADE,
        related_name='chunks'
    )
    chunk_index = models.IntegerField()
    text = models.TextField()
    token_count = models.IntegerField()
    embedding_384 = VectorField(dimensions=384, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rag_chunks_small"
        indexes = [
            models.Index(fields=["section", "chunk_index"]),
        ]

# Similar structures for Medium (768d) and Large (1024d)
```

### 2. Chunking Service

```python
# upper_lake/chunking/service.py

from django.db import transaction
from typing import List, Dict
import tiktoken
from dataclasses import dataclass

@dataclass
class ChunkResult:
    sections_processed: int
    chunks_created: int
    total_tokens: int

SIZE_CONFIG = {
    'small_384': {
        'chunk_size': 200,
        'chunk_overlap': 30,
        'section_model': RAGFilingSectionSmall,
        'chunk_model': RAGChunkSmall,
    },
    'medium_768': {
        'chunk_size': 300,
        'chunk_overlap': 50,
        'section_model': RAGFilingSectionMedium,
        'chunk_model': RAGChunkMedium,
    },
    'large_1024': {
        'chunk_size': 450,
        'chunk_overlap': 70,
        'section_model': RAGFilingSectionLarge,
        'chunk_model': RAGChunkLarge,
    }
}

class TenKChunker:
    """Service to chunk 10-K filings and store in RAG tables"""
    
    def __init__(self, size='small_384'):
        self.config = SIZE_CONFIG[size]
        self.tokenizer = tiktoken.get_encoding('cl100k_base')
    
    def chunk_filing(self, filing_id: int) -> ChunkResult:
        """Chunk a single filing across all sizes"""
        filing = TenKData.objects.get(id=filing_id)
        
        sections_processed = 0
        chunks_created = 0
        total_tokens = 0
        
        # Process each section
        for section_col in SECTION_COLUMNS:
            text = getattr(filing, section_col)
            if not text or len(text.strip()) < 100:
                continue
            
            # Create section record
            section = self.config['section_model'].objects.create(
                filing_type='10-K',
                ticker=filing.ticker,
                filing_date=filing.filing_date,
                filing_url=filing.filing_url,
                source_table='raw_ten_k_data',
                source_column=section_col,
                section_name=self._get_section_name(section_col),
                full_text=text
            )
            
            # Chunk the text
            chunks = self._chunk_text(text)
            
            # Create chunk records
            chunk_objs = [
                self.config['chunk_model'](
                    section=section,
                    chunk_index=i,
                    text=chunk,
                    token_count=len(self.tokenizer.encode(chunk))
                )
                for i, chunk in enumerate(chunks)
            ]
            
            self.config['chunk_model'].objects.bulk_create(chunk_objs)
            
            sections_processed += 1
            chunks_created += len(chunks)
            total_tokens += sum(c.token_count for c in chunk_objs)
        
        return ChunkResult(sections_processed, chunks_created, total_tokens)
    
    def _chunk_text(self, text: str) -> List[str]:
        """Chunk text into overlapping segments"""
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        chunk_size = self.config['chunk_size']
        overlap = self.config['chunk_overlap']
        
        for i in range(0, len(tokens), chunk_size - overlap):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks
```

### 3. Embedding Service

```python
# upper_lake/services/embedding_service.py

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

MODELS = {
    'small_384': {
        'name': 'BAAI/bge-small-en-v1.5',
        'dimensions': 384
    },
    'medium_768': {
        'name': 'BAAI/bge-base-en-v1.5',
        'dimensions': 768
    },
    'large_1024': {
        'name': 'BAAI/bge-large-en-v1.5',
        'dimensions': 1024
    }
}

_models = {}

def get_model(size: str) -> SentenceTransformer:
    """Lazy load embedding model"""
    if size not in _models:
        model_name = MODELS[size]['name']
        _models[size] = SentenceTransformer(model_name)
    return _models[size]

def generate_embeddings(texts: List[str], size='small_384') -> np.ndarray:
    """Generate embeddings for a list of texts"""
    model = get_model(size)
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    return embeddings

def generate_query_embedding(query: str, size='small_384') -> List[float]:
    """Generate embedding for a single query"""
    embeddings = generate_embeddings([query], size=size)
    return embeddings[0].tolist()
```

### 4. Vector Search Service

```python
# upper_lake/services/vector_search.py

from typing import List, Dict, Optional
from django.db import connection
from .embedding_service import generate_query_embedding

class VectorSearchService:
    """Vector similarity search using pgvector"""
    
    def __init__(self, embedding_size='small_384'):
        self.size = embedding_size
        self.table_map = {
            'small_384': ('rag_chunks_small', 'embedding_384'),
            'medium_768': ('rag_chunks_medium', 'embedding_768'),
            'large_1024': ('rag_chunks_large', 'embedding_1024'),
        }
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        ticker: Optional[str] = None,
        year: Optional[int] = None,
        section: Optional[str] = None
    ) -> List[Dict]:
        """Search for similar chunks with optional filters"""
        
        # Generate query embedding
        query_embedding = generate_query_embedding(query, self.size)
        
        # Get table names
        chunk_table, embedding_col = self.table_map[self.size]
        section_table = chunk_table.replace('chunks', 'filing_sections')
        
        # Build SQL query
        sql = f"""
            SELECT 
                c.id,
                c.text,
                c.token_count,
                s.ticker,
                s.filing_date,
                s.section_name,
                1 - (c.{embedding_col} <=> %s::vector) AS similarity
            FROM {chunk_table} c
            JOIN {section_table} s ON c.section_id = s.id
            WHERE 1=1
        """
        
        params = [query_embedding]
        
        # Add filters
        if ticker:
            sql += " AND s.ticker = %s"
            params.append(ticker.upper())
        
        if year:
            sql += " AND EXTRACT(YEAR FROM s.filing_date) = %s"
            params.append(year)
        
        if section:
            sql += " AND s.section_name ILIKE %s"
            params.append(f"%{section}%")
        
        sql += f" ORDER BY c.{embedding_col} <=> %s::vector LIMIT %s"
        params.extend([query_embedding, top_k])
        
        # Execute
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return results
```

### 5. QA Service

```python
# upper_lake/services/qa_service.py

from typing import Dict, Optional
import requests
from .vector_search import VectorSearchService

class FinancialQAService:
    """RAG Q&A orchestration"""
    
    def __init__(self, ollama_model='tinyllama', embedding_size='small_384'):
        self.model = ollama_model
        self.ollama_url = 'http://localhost:11434'
        self.search_service = VectorSearchService(embedding_size)
    
    def ask(
        self,
        question: str,
        ticker: Optional[str] = None,
        year: Optional[int] = None,
        section: Optional[str] = None,
        top_k: int = 5,
        temperature: float = 0.3
    ) -> Dict:
        """Answer a question using RAG"""
        
        # Step 1: Retrieve relevant chunks
        chunks = self.search_service.search(
            query=question,
            top_k=top_k,
            ticker=ticker,
            year=year,
            section=section
        )
        
        if not chunks:
            return {
                'question': question,
                'answer': "No relevant information found.",
                'sources': [],
                'metadata': {'cost': 0, 'tokens': 0}
            }
        
        # Step 2: Generate answer with LLM
        answer_data = self._generate_answer(question, chunks, temperature)
        
        # Step 3: Format response
        return {
            'question': question,
            'answer': answer_data['answer'],
            'sources': self._format_sources(chunks),
            'metadata': {
                'num_chunks': len(chunks),
                'cost': 0.0,
                'tokens': answer_data.get('tokens', 0),
                'avg_similarity': sum(c['similarity'] for c in chunks) / len(chunks),
                'model': self.model
            }
        }
    
    def _generate_answer(self, question: str, chunks: List[Dict], temp: float) -> Dict:
        """Generate answer using Ollama"""
        
        # Build context
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}] {chunk['ticker']} - {chunk['filing_date']} "
                f"({chunk['section_name']})\n{chunk['text']}"
            )
        
        context = "\n\n".join(context_parts)
        
        # Build prompt
        prompt = f"""You are a financial analyst assistant. Answer based ONLY on the provided SEC 10-K excerpts.

Rules:
- Cite sources using [Source 1], [Source 2], etc.
- Be concise and accurate
- If information isn't in the excerpts, say so

Context:
{context}

Question: {question}

Answer:"""
        
        # Call Ollama
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temp,
                    "num_predict": 500
                }
            },
            timeout=120
        )
        
        result = response.json()
        
        return {
            'answer': result['response'].strip(),
            'tokens': result.get('eval_count', 0)
        }
    
    def _format_sources(self, chunks):
        return [
            {
                'number': i + 1,
                'ticker': chunk['ticker'],
                'filing_date': str(chunk['filing_date']),
                'section': chunk['section_name'],
                'similarity': round(chunk['similarity'], 3)
            }
            for i, chunk in enumerate(chunks)
        ]
```

### 6. FastAPI Application

```python
# upper_lake/api/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from upper_lake.services.qa_service import FinancialQAService

app = FastAPI(
    title="Financial 10-K Search API",
    description="RAG-based semantic search through SEC 10-K filings",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

qa_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global qa_service
    
    ollama_model = os.getenv('OLLAMA_MODEL', 'tinyllama')
    embedding_size = os.getenv('EMBEDDING_SIZE', 'small_384')
    
    qa_service = FinancialQAService(
        ollama_model=ollama_model,
        embedding_size=embedding_size
    )
    
    print(f"✓ API ready with {ollama_model} and {embedding_size} embeddings")

class QueryRequest(BaseModel):
    question: str
    ticker: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None
    top_k: int = 5

@app.get("/")
async def root():
    return {
        "message": "Financial 10-K Search API",
        "endpoints": {
            "health": "/health",
            "ask": "/ask (POST)",
            "stats": "/stats",
            "docs": "/docs"
        }
    }

@app.post("/ask")
async def ask_question(request: QueryRequest):
    """Ask a question about SEC 10-K filings"""
    
    if qa_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = qa_service.ask(
            question=request.question,
            ticker=request.ticker,
            year=request.year,
            section=request.section,
            top_k=request.top_k
        )
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/stats")
async def stats():
    """Get database statistics"""
    from upper_lake.models import RAGChunkSmall, RAGFilingSectionSmall
    
    return {
        'total_sections': RAGFilingSectionSmall.objects.count(),
        'total_chunks': RAGChunkSmall.objects.count(),
        'chunks_with_embeddings': RAGChunkSmall.objects.filter(
            embedding_384__isnull=False
        ).count(),
        'unique_tickers': RAGFilingSectionSmall.objects.values(
            'ticker'
        ).distinct().count()
    }
```

---

## Setup and Deployment

### Local Development

#### Prerequisites
```bash
# Install PostgreSQL with pgvector
brew install postgresql@15
brew install pgvector

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull tinyllama
```

#### Installation
```bash
# Clone repo
git clone <repo-url>
cd alpine-finance/django_project

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
createdb alfin_lakes
psql alfin_lakes -c "CREATE EXTENSION vector;"

# Run migrations
python manage.py migrate

# Chunk filings (one-time)
python manage.py chunk_filings --size small_384 --limit 100

# Generate embeddings (one-time)
python manage.py generate_embeddings --size small_384 --batch-size 32

# Start API
uvicorn upper_lake.api.main:app --reload
```

### Docker Deployment

```yaml
# docker-compose.yml

version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: alfin_lakes
      POSTGRES_USER: amit_chandna
      POSTGRES_PASSWORD: oX6PozwzvIVfSG
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U amit_chandna"]
      interval: 10s
      timeout: 5s
      retries: 5

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3

  api:
    build: .
    depends_on:
      - postgres
      - ollama
    environment:
      DATABASE_URL: postgresql://amit_chandna:oX6PozwzvIVfSG@postgres:5432/alfin_lakes
      OLLAMA_URL: http://ollama:11434
      OLLAMA_MODEL: tinyllama
      EMBEDDING_SIZE: small_384
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    command: >
      bash -c "
        python manage.py migrate &&
        uvicorn upper_lake.api.main:app --host 0.0.0.0 --port 8000
      "

volumes:
  postgres-data:
  ollama-data:
```

```bash
# Deploy
docker-compose up -d

# View logs
docker-compose logs -f api

# Run commands
docker-compose exec api python manage.py chunk_filings --size small_384
```

---

## Usage Examples

### API Usage

```bash
# Health check
curl http://localhost:8000/health

# Statistics
curl http://localhost:8000/stats

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are Apples main AI risks?",
    "ticker": "AAPL",
    "year": 2023,
    "top_k": 5
  }'
```

### CLI Chat

```bash
# Start interactive chat
python manage.py chat

# With specific ticker
python manage.py chat --ticker AAPL

# With specific model
python manage.py chat --model phi3:mini
```

### Django Shell

```python
# Start shell
python manage.py shell

# Search example
from upper_lake.services.vector_search import VectorSearchService

search = VectorSearchService('small_384')
results = search.search(
    query="What are the cybersecurity risks?",
    ticker="MSFT",
    year=2023,
    top_k=3
)

for r in results:
    print(f"{r['ticker']} - {r['filing_date']}")
    print(f"Similarity: {r['similarity']:.3f}")
    print(f"{r['text'][:200]}...")
    print()
```

---

## Management Commands

### Chunking
```bash
# Chunk all filings for all sizes
python manage.py chunk_filings --size all

# Chunk specific size
python manage.py chunk_filings --size small_384 --limit 1000

# Resume from specific ID
python manage.py chunk_filings --size medium_768 --start-id 5000
```

### Embeddings
```bash
# Generate embeddings for all chunks
python manage.py generate_embeddings --size small_384

# Batch processing
python manage.py generate_embeddings --size large_1024 --batch-size 16

# GPU acceleration
python manage.py generate_embeddings --size medium_768 --device cuda
```

### Database Maintenance
```bash
# Count chunks
python manage.py dbshell
SELECT COUNT(*) FROM rag_chunks_small WHERE embedding_384 IS NOT NULL;

# Rebuild vector index
python manage.py dbshell
REINDEX INDEX idx_chunks_embedding_cosine;

# Analyze tables
ANALYZE rag_chunks_small;
```

---

## Configuration

### Environment Variables

```bash
# .env

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/alfin_lakes

# Ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama

# Embeddings
EMBEDDING_SIZE=small_384
EMBEDDING_DEVICE=cpu

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### Django Settings

```python
# django_project/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'alfin_lakes',
        'USER': 'amit_chandna',
        'PASSWORD': 'oX6PozwzvIVfSG',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'upper_lake',
]
```

---

## Performance Optimization

### Vector Search Optimization

```sql
-- Create indexes
CREATE INDEX idx_chunks_embedding_ivfflat 
    ON rag_chunks_small 
    USING ivfflat (embedding_384 vector_cosine_ops)
    WITH (lists = 100);

-- Tune parameters
SET ivfflat.probes = 10;

-- Analyze query performance
EXPLAIN ANALYZE
SELECT * FROM rag_chunks_small
ORDER BY embedding_384 <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;
```

### Embedding Generation

```bash
# Use GPU for faster generation
python manage.py generate_embeddings --device cuda --batch-size 64

# Parallel processing
python manage.py generate_embeddings --workers 4
```

### API Performance

```python
# Add caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_search(query: str, ticker: str, year: int):
    return search_service.search(query, ticker=ticker, year=year)
```

---

## Troubleshooting

### Common Issues

#### Ollama Connection Errors
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve

# Pull model
ollama pull tinyllama
```

#### PostgreSQL Connection
```bash
# Check PostgreSQL status
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -U amit_chandna -d alfin_lakes -c "SELECT 1"

# Check pgvector
psql -d alfin_lakes -c "SELECT * FROM pg_extension WHERE extname = 'vector'"
```

#### Memory Issues
```bash
# Use smaller models
export OLLAMA_MODEL=qwen2.5:1.5b

# Reduce batch size
python manage.py generate_embeddings --batch-size 8

# Use CPU-only
export EMBEDDING_DEVICE=cpu
```

---

## Future Enhancements

### Short-Term
- [ ] Add query caching with Redis
- [ ] Implement authentication (API keys)
- [ ] Add rate limiting
- [ ] Create web frontend
- [ ] Add monitoring/logging

### Medium-Term
- [ ] Multi-query support (compare companies)
- [ ] Temporal analysis (trends over years)
- [ ] Export results to PDF/Excel
- [ ] Add more embedding models
- [ ] Implement hybrid search (sparse + dense)

### Long-Term
- [ ] Fine-tune LLM on financial domain
- [ ] Add graph database for relationships
- [ ] Implement evaluation framework
- [ ] Add A/B testing infrastructure
- [ ] Deploy to production (AWS/GCP)

---

## Project Metrics

### Dataset Scale
- **Filings**: 67,440 10-K documents
- **Companies**: 12,000+ unique tickers
- **Sections**: ~400,000 extracted sections
- **Chunks**: ~2,000,000 text chunks
- **Embeddings**: ~2M vectors (per size)

### Performance
- **Query Latency**: 2-5 seconds (including LLM generation)
- **Vector Search**: <100ms for top-10 results
- **Embedding Generation**: ~500 chunks/min (CPU)
- **Storage**: ~50GB total (database + embeddings)

### Cost
- **Infrastructure**: $0 (local development)
- **LLM**: $0 (Ollama local)
- **Embeddings**: $0 (sentence-transformers)
- **Deployment**: ~$20/month (Docker on AWS EC2)

---

## References

### Documentation
- [pgvector](https://github.com/pgvector/pgvector)
- [sentence-transformers](https://www.sbert.net/)
- [Ollama](https://ollama.ai/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Django](https://docs.djangoproject.com/)

### Related Projects
- LangChain
- LlamaIndex
- Pinecone
- Weaviate

---

## License

MIT License

---

## Contact

For questions or issues, contact: achandna2@gmail.com

---

**Last Updated**: January 5, 2026
**Version**: 1.0.0
**Status**: Production Ready
