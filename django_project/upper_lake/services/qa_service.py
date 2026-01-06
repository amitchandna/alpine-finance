"""
Enhanced Q&A service with improved citations.
Replace your existing qa_service.py with this version.
"""

from typing import Dict, Optional, List
import requests
import re
from .vector_search import VectorSearchService


class FinancialQAService:
    """RAG Q&A orchestration service with enhanced citations."""

    def __init__(
        self,
        ollama_model: str = 'tinyllama',
        embedding_size: str = 'small_384',
        ollama_url: str = 'http://localhost:11434'
    ):
        self.model = ollama_model
        self.ollama_url = ollama_url
        self.search_service = VectorSearchService(embedding_size)

    def ask(
        self,
        question: str,
        top_k: int = 5,
        temperature: float = 0.3
    ) -> Dict:
        """
        Answer a question using RAG with proper citations.

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
        # Auto-detect ticker if not provided

        # Step 1: Retrieve relevant chunks
        chunks = self.search_service.search(
            query=question,
            top_k=top_k
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

        # Step 3: Format response with enhanced source info
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

    def _extract_ticker(self, query: str) -> Optional[str]:
        """Extract ticker symbol from query."""
        ticker_pattern = r'\b([A-Z]{2,5})\b'
        matches = re.findall(ticker_pattern, query)

        if not matches:
            return None

        # Filter out common words that look like tickers
        common_words = {
            'AI', 'IT', 'US', 'CEO', 'CFO', 'SEC', 'IPO', 'LLC',
            'MD', 'MA', 'PM', 'AM', 'FAQ', 'API', 'USA', 'UK'
        }

        for match in matches:
            if match not in common_words:
                return match

        return None

    def _generate_answer(
        self,
        question: str,
        chunks: List[Dict],
        temperature: float
    ) -> Dict:
        """Generate answer using Ollama with strong citation requirements."""

        # Build context with clear source markers
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}]\n"
                f"Company: {chunk['ticker']}\n"
                f"Date: {chunk['filing_date']}\n"
                f"Section: {chunk['section_name']}\n"
                f"Content: {chunk['text']}\n"
            )

        context = "\n".join(context_parts)

        # Enhanced prompt with stronger citation requirements
        prompt = f"""You are a financial analyst assistant answering questions about SEC 10-K filings.

CRITICAL RULES:
1. Answer ONLY using information from the sources below
2. ALWAYS cite your sources using [Source 1], [Source 2], etc.
3. Every factual claim MUST have a citation
4. If multiple sources support a point, cite all of them: [Source 1, 2]
5. If information is not in the sources, say "This information is not available in the provided filings"

FORMAT YOUR ANSWER LIKE THIS:
- Start with a direct answer to the question
- Support each point with citations
- Use bullet points for multiple risks/items
- Each bullet point should have citations

Example:
The main risks include:
- Regulatory compliance challenges [Source 1]
- Supply chain disruptions affecting operations [Source 2, 3]
- Increasing competition in the market [Source 1]

SOURCES:
{context}

QUESTION: {question}

ANSWER (with citations):"""

        try:
            print(f"\n🔍 Calling Ollama ({self.model})...")

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": 800,  # More tokens for detailed citations
                        "top_p": 0.9,
                        "top_k": 40
                    }
                },
                timeout=120
            )

            if response.status_code != 200:
                error_text = response.text if response.text else "Unknown error"
                return {
                    'answer': f"❌ Ollama Error {response.status_code}: {error_text}",
                    'tokens': 0
                }

            result = response.json()
            answer_text = result['response'].strip()

            # Verify citations are present
            citations_found = len(re.findall(r'\[Source \d+(?:,\s*\d+)*\]', answer_text))

            if citations_found == 0:
                answer_text = (
                    "⚠️ Note: The model didn't provide citations. Here's the answer:\n\n"
                    + answer_text +
                    "\n\n(See source list below for reference documents)"
                )

            return {
                'answer': answer_text,
                'tokens': result.get('eval_count', 0),
                'citations_count': citations_found
            }

        except requests.exceptions.ConnectionError:
            return {
                'answer': "⚠️ Error: Cannot connect to Ollama. Is it running? (ollama serve)",
                'tokens': 0
            }
        except requests.exceptions.Timeout:
            return {
                'answer': "⚠️ Error: Request timed out after 120s. Try a simpler question.",
                'tokens': 0
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'answer': f"Error: {str(e)}",
                'tokens': 0
            }

    def _format_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Format source citations with full details."""
        sources = []
        for i, chunk in enumerate(chunks, 1):
            sources.append({
                'number': i,
                'ticker': chunk['ticker'],
                'filing_date': str(chunk['filing_date']),
                'section': chunk['section_name'],
                'similarity': round(chunk['similarity'], 3),
                'preview': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text']
            })
        return sources