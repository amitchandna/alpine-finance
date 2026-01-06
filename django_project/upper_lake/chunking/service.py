"""
Chunking service for processing 10-K filings.
"""

from django.db import transaction
from typing import List, Dict
from dataclasses import dataclass
import logging

from upper_lake.models import (
    TenKData,
    RAGFilingSectionSmall, RAGChunkSmall,
    RAGFilingSectionMedium, RAGChunkMedium,
    RAGFilingSectionLarge, RAGChunkLarge,
)
from .utils import (
    SimpleTextSplitter,
    TokenCounter,
    clean_text,
    get_section_name,
    SECTION_COLUMNS
)

logger = logging.getLogger(__name__)


@dataclass
class ChunkResult:
    """Result of chunking operation."""
    sections_processed: int
    chunks_created: int
    total_tokens: int


# Configuration for each embedding size
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
    """Service to chunk 10-K filings."""
    
    def __init__(self, size: str = 'small_384'):
        if size not in SIZE_CONFIG:
            raise ValueError(f"Invalid size: {size}. Choose from {list(SIZE_CONFIG.keys())}")
        
        self.config = SIZE_CONFIG[size]
        self.splitter = SimpleTextSplitter(
            chunk_size=self.config['chunk_size'],
            chunk_overlap=self.config['chunk_overlap']
        )
        self.tokenizer = TokenCounter()
    
    @transaction.atomic
    def chunk_filing(self, filing_id: int) -> ChunkResult:
        """
        Chunk a single filing.
        
        Args:
            filing_id: ID of TenKData record
        
        Returns:
            ChunkResult with statistics
        """
        try:
            filing = TenKData.objects.get(id=filing_id)
        except TenKData.DoesNotExist:
            raise ValueError(f"Filing {filing_id} not found")
        
        sections_processed = 0
        chunks_created = 0
        total_tokens = 0
        
        # Process each section
        for section_col in SECTION_COLUMNS:
            text = getattr(filing, section_col, None)
            
            # Skip empty or short sections
            if not text or len(text.strip()) < 100:
                continue
            
            # Clean text
            text = clean_text(text)
            
            # Create section record
            section = self.config['section_model'].objects.create(
                filing_type='10-K',
                ticker=filing.ticker,
                filing_date=filing.filing_date,
                filing_url=filing.filing_url,
                source_table='raw_ten_k_data',
                source_column=section_col,
                section_name=get_section_name(section_col),
                full_text=text
            )
            
            # Chunk the text
            chunks = self.splitter.split_text(text)
            
            # Create chunk records
            chunk_objs = []
            for i, chunk in enumerate(chunks):
                token_count = self.tokenizer.count_tokens(chunk)
                chunk_objs.append(
                    self.config['chunk_model'](
                        section=section,
                        chunk_index=i,
                        text=chunk,
                        token_count=token_count
                    )
                )
                total_tokens += token_count
            
            # Bulk create chunks
            self.config['chunk_model'].objects.bulk_create(chunk_objs)
            
            sections_processed += 1
            chunks_created += len(chunks)
            
            logger.info(
                f"Processed {filing.ticker} {section_col}: "
                f"{len(chunks)} chunks, {total_tokens} tokens"
            )
        
        return ChunkResult(sections_processed, chunks_created, total_tokens)
    
    def chunk_batch(self, filing_ids: List[int]) -> Dict:
        """
        Chunk multiple filings.
        
        Args:
            filing_ids: List of filing IDs
        
        Returns:
            Summary statistics
        """
        total_sections = 0
        total_chunks = 0
        total_tokens = 0
        failures = []
        
        for filing_id in filing_ids:
            try:
                result = self.chunk_filing(filing_id)
                total_sections += result.sections_processed
                total_chunks += result.chunks_created
                total_tokens += result.total_tokens
            except Exception as e:
                logger.error(f"Failed to chunk filing {filing_id}: {e}")
                failures.append({'filing_id': filing_id, 'error': str(e)})
        
        return {
            'total_sections': total_sections,
            'total_chunks': total_chunks,
            'total_tokens': total_tokens,
            'failures': failures
        }
