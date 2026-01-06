# Alpine Finance

A production-ready RAG (Retrieval Augmented Generation) system for analyzing SEC 10-K financial filings using LLMs and vector search.

## Features

- **Semantic Search**: Query financial documents using natural language
- **Multi-embedding Support**: Small (384d), Medium (768d), and Large (1024d) embeddings
- **Local LLM Integration**: Ollama-based answer generation (CPU-friendly)
- **Production FastAPI Backend**: RESTful API with health checks and statistics
- **Django ORM**: PostgreSQL + pgvector for data management
- **Configurable Models**: Hot-swappable embedding and LLM models

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 15+ with pgvector extension
- Ollama (for local LLM)

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd alpine-finance

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd django_project
pip install -r requirements.txt

# Setup database
createdb alfin_lakes
psql alfin_lakes -c "CREATE EXTENSION vector;"

# Run migrations
python manage.py migrate

# Start Ollama (in separate terminal)
ollama serve
ollama pull tinyllama

# Start API
uvicorn upper_lake.api.main:app --reload
```

### Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Run management commands
docker-compose exec api python manage.py chunk_filings --size small_384
docker-compose exec api python manage.py generate_embeddings --size small_384
```

## Usage

### API Examples

```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are Apples main AI risks?",
    "ticker": "AAPL",
    "year": 2023
  }'

# Get statistics
curl http://localhost:8000/stats
```

### CLI Chat

```bash
# Interactive chat
python manage.py chat

# With filters
python manage.py chat --ticker AAPL --year 2023
```

## Project Structure

```
alpine-finance/
├── django_project/
│   ├── django_project/        # Django settings
│   ├── upper_lake/            # Main application
│   │   ├── api/               # FastAPI application
│   │   ├── services/          # Business logic
│   │   ├── chunking/          # Text processing
│   │   ├── management/        # Django commands
│   │   └── models.py          # Database models
│   ├── manage.py
│   └── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Documentation

See [ALPINE_FINANCE_PROJECT_RECONSTRUCTION.md](ALPINE_FINANCE_PROJECT_RECONSTRUCTION.md) for complete documentation including:
- Architecture diagrams
- Database schema
- API reference
- Management commands
- Troubleshooting guide

## Tech Stack

- **Backend**: Python, Django, FastAPI
- **Database**: PostgreSQL with pgvector
- **Embeddings**: sentence-transformers
- **LLM**: Ollama (tinyllama, phi3, qwen)
- **Deployment**: Docker Compose

## Dataset

- 67,440 SEC 10-K filings
- 12,000+ unique tickers
- ~2M text chunks
- Multiple embedding dimensions

## License

MIT

## Contact

achandna2@gmail.com
