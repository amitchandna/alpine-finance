# Alpine Finance - Project Structure

```
alpine-finance/
│
├── README.md                                  # Main project README
├── SETUP.md                                   # Detailed setup instructions
├── ALPINE_FINANCE_PROJECT_RECONSTRUCTION.md  # Complete documentation
├── .env.example                               # Environment variables template
├── .gitignore                                 # Git ignore rules
│
├── Dockerfile                                 # Docker container definition
├── docker-compose.yml                         # Multi-container orchestration
│
└── django_project/                            # Main Django project
    │
    ├── manage.py                              # Django management script
    ├── requirements.txt                       # Python dependencies
    │
    ├── django_project/                        # Django configuration
    │   ├── __init__.py
    │   ├── settings.py                        # Django settings
    │   ├── urls.py                            # URL routing
    │   └── wsgi.py                            # WSGI application
    │
    └── upper_lake/                            # Main Django app
        │
        ├── __init__.py
        ├── models.py                          # Database models (RAG tables)
        │
        ├── api/                               # FastAPI application
        │   ├── __init__.py
        │   └── main.py                        # API endpoints and routes
        │
        ├── services/                          # Business logic services
        │   ├── __init__.py
        │   ├── embedding_service.py           # Embedding generation
        │   ├── vector_search.py               # pgvector search
        │   └── qa_service.py                  # RAG orchestration
        │
        ├── chunking/                          # Text processing
        │   ├── __init__.py
        │   ├── service.py                     # Chunking logic
        │   └── utils.py                       # Helper functions
        │
        ├── management/                        # Django management commands
        │   ├── __init__.py
        │   └── commands/
        │       ├── __init__.py
        │       ├── chunk_filings.py           # Chunk 10-K filings
        │       ├── generate_embeddings.py     # Generate embeddings
        │       └── chat.py                    # Interactive chat CLI
        │
        └── migrations/                        # Database migrations
            └── __init__.py
```

## Key Files Description

### Configuration Files
- **settings.py**: Django configuration including database connection
- **requirements.txt**: All Python package dependencies
- **.env.example**: Template for environment variables
- **docker-compose.yml**: Multi-container setup with PostgreSQL + Ollama + API

### Core Application Files

#### Models (`models.py`)
- `TenKData`: Original 10-K filings
- `RAGFilingSectionSmall/Medium/Large`: Extracted sections
- `RAGChunkSmall/Medium/Large`: Text chunks with embeddings

#### Services
- **embedding_service.py**: sentence-transformers integration
- **vector_search.py**: pgvector similarity search
- **qa_service.py**: Complete RAG pipeline with LLM

#### Chunking
- **service.py**: Main chunking logic for all sizes
- **utils.py**: Text cleaning, tokenization, helpers

#### API (`api/main.py`)
- FastAPI application with endpoints:
  - `GET /`: Root info
  - `POST /ask`: Query endpoint
  - `GET /health`: Health check
  - `GET /stats`: Database statistics

#### Management Commands
- **chunk_filings.py**: Process 10-K filings into chunks
- **generate_embeddings.py**: Create vector embeddings
- **chat.py**: Interactive CLI for testing

## Data Flow

```
1. Raw Data (raw_ten_k_data)
   ↓
2. Chunking (chunk_filings command)
   ↓
3. RAGFilingSection + RAGChunk tables
   ↓
4. Embedding Generation (generate_embeddings command)
   ↓
5. Chunks with embeddings (vector fields populated)
   ↓
6. Query API
   ↓
7. Vector search → LLM → Answer
```

## Total Files: 29

- **Python files**: 19
- **Configuration files**: 6
- **Documentation files**: 4

## Database Tables: 9

- `raw_ten_k_data` (existing)
- `rag_filing_sections_small/medium/large` (3 tables)
- `rag_chunks_small/medium/large` (3 tables)
- Django migrations tables (2 tables)

## Total Lines of Code: ~2,500

- Models: ~200 lines
- Services: ~800 lines
- Chunking: ~400 lines
- API: ~200 lines
- Commands: ~300 lines
- Configuration: ~200 lines
- Documentation: ~400 lines
