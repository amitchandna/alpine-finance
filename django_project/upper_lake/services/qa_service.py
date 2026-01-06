"""
Q&A service orchestrating RAG pipeline.
"""

from typing import Dict, Optional, List
import requests
from .vector_search import VectorSearchService


class FinancialQAService:
    """RAG Q&A orchestration service."""
    
    def __init__(
        self,
        ollama_model: str = 'llama3.2:1b',
        embedding_size: str = 'small_384',
        ollama_url: str = 'http://localhost:11434'
    ):
        self.model = ollama_model
        self.ollama_url = ollama_url
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
        """
        Answer a question using RAG.
        
        Args:
            question: User's question
            ticker: Filter by ticker
            year: Filter by year
            section: Filter by section
            top_k: Number of chunks to retrieve
            temperature: LLM temperature
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
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
                'answer': "No relevant information found. Try different filters or keywords.",
                'sources': [],
                'metadata': {'cost': 0, 'tokens': 0, 'num_chunks': 0}
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
                'cost': 0.0,  # Free with Ollama
                'tokens': answer_data.get('tokens', 0),
                'avg_similarity': sum(c['similarity'] for c in chunks) / len(chunks),
                'model': self.model
            }
        }
    
    def _generate_answer(
        self,
        question: str,
        chunks: List[Dict],
        temperature: float
    ) -> Dict:
        """Generate answer using Ollama."""
        
        # Build context from chunks
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
- Use financial terminology appropriately
- If information isn't in the excerpts, say so clearly

Context from SEC 10-K filings:
{context}

Question: {question}

Answer:"""
        
        try:
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": 500
                    }
                },
                timeout=120
            )
            print(f"🔍 DEBUG: Response status: {response.status_code}")
            print(f"🔍 DEBUG: Response body: {response.text[:200]}")
            
            if response.status_code != 200:
                return {
                    'answer': f"Error: Ollama returned status {response.status_code}",
                    'tokens': 0
                }
            
            result = response.json()
            
            return {
                'answer': result['response'].strip(),
                'tokens': result.get('eval_count', 0)
            }
        
        except requests.exceptions.ConnectionError:
            return {
                'answer': "⚠️ Error: Ollama is not running. Start it with: ollama serve",
                'tokens': 0
            }
        except requests.exceptions.Timeout:
            return {
                'answer': "⚠️ Error: Request timed out. Try a simpler question or restart Ollama.",
                'tokens': 0
            }
        except Exception as e:
            return {
                'answer': f"Error generating answer: {str(e)}",
                'tokens': 0
            }
    
    def _format_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Format source citations."""
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
