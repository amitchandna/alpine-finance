"""
Vector similarity search using pgvector.
"""

from typing import List, Dict, Optional
from django.db import connection
from .embedding_service import generate_query_embedding


class VectorSearchService:
    """Vector similarity search service."""
    
    def __init__(self, embedding_size: int = 384):
        self.size = embedding_size
        self.table_map = {
            'small_384': ('rag_chunks_small', 'rag_filing_sections_small', 'embedding_384'),
            'medium_768': ('rag_chunks_medium', 'rag_filing_sections_medium', 'embedding_768'),
            'large_1024': ('rag_chunks_large', 'rag_filing_sections_large', 'embedding_1024'),
        }
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        ticker: Optional[str] = None,
        year: Optional[int] = None,
        section: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for similar chunks with optional filters.
        
        Args:
            query: Search query
            top_k: Number of results to return
            ticker: Filter by ticker (e.g., 'AAPL')
            year: Filter by year
            section: Filter by section name
        
        Returns:
            List of matching chunks with metadata
        """
        # Generate query embedding
        query_embedding = generate_query_embedding(query, self.size)
        
        # Get table names
        chunk_table, section_table, embedding_col = self.table_map[self.size]
        
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
            WHERE c.{embedding_col} IS NOT NULL
        """
        
        params = [query_embedding]
        
        # Add filters
        if ticker:
            sql += " AND UPPER(s.ticker) = UPPER(%s)"
            params.append(ticker)
        
        if year:
            sql += " AND EXTRACT(YEAR FROM s.filing_date) = %s"
            params.append(year)
        
        if section:
            sql += " AND s.section_name ILIKE %s"
            params.append(f"%{section}%")
        
        # Order by similarity and limit
        sql += f" ORDER BY c.{embedding_col} <=> %s::vector LIMIT %s"
        params.extend([query_embedding, top_k])
        
        # Execute query
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return results
