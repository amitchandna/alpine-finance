"""
FastAPI application for Alpine Finance.
"""

import os
import sys
import django

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from upper_lake.services.qa_service import FinancialQAService
from upper_lake.models import RAGChunkSmall, RAGFilingSectionSmall

app = FastAPI(
    title="Alpine Finance API",
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

# Global service instance
qa_service = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global qa_service
    
    try:
        print("\n" + "="*60)
        print("Initializing Alpine Finance API...")
        print("="*60)
        
        ollama_model = os.getenv('OLLAMA_MODEL', 'tinyllama')
        embedding_size = os.getenv('EMBEDDING_SIZE', 'small_384')
        ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        
        print(f"Using Ollama model: {ollama_model}")
        print(f"Using embedding size: {embedding_size}")
        
        qa_service = FinancialQAService(
            ollama_model=ollama_model,
            embedding_size=embedding_size,
            ollama_url=ollama_url
        )
        
        print("✓ QA service initialized successfully")
        print("✓ API ready to accept requests")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Failed to initialize: {e}\n")
        import traceback
        traceback.print_exc()


class QueryRequest(BaseModel):
    """Query request model."""
    question: str
    ticker: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None
    top_k: int = 5
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are Apple's main AI risks?",
                "ticker": "AAPL",
                "year": 2023,
                "top_k": 5
            }
        }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Alpine Finance API",
        "description": "RAG-based semantic search through SEC 10-K filings",
        "endpoints": {
            "health": "/health - Check API status",
            "ask": "/ask (POST) - Ask a question",
            "stats": "/stats - Get database statistics",
            "docs": "/docs - Interactive API documentation"
        },
        "version": "1.0.0"
    }


@app.post("/ask")
async def ask_question(request: QueryRequest):
    """
    Ask a question about SEC 10-K filings.
    
    Args:
        request: Query parameters
    
    Returns:
        Answer with sources and metadata
    """
    if qa_service is None:
        raise HTTPException(
            status_code=503,
            detail="Service not initialized. Check server logs."
        )
    
    try:
        print(f"\n{'='*60}")
        print(f"📝 Query: {request.question[:100]}...")
        if request.ticker:
            print(f"   Ticker: {request.ticker}")
        if request.year:
            print(f"   Year: {request.year}")
        print(f"{'='*60}\n")
        
        result = qa_service.ask(
            question=request.question,
            ticker=request.ticker,
            year=request.year,
            section=request.section,
            top_k=request.top_k
        )
        
        return result
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "alpine-finance"
    }


@app.get("/stats")
async def get_stats():
    """Get database statistics."""
    try:
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
    except Exception as e:
        return {
            'error': 'Failed to fetch statistics',
            'details': str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
