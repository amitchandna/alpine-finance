"""
Utilities for text chunking.
"""

import re
import tiktoken
from typing import List


# Section name mapping
SECTION_MAPPING = {
    'section_one': 'Item 1 - Business',
    'section_one_a': 'Item 1A - Risk Factors',
    'section_one_b': 'Item 1B - Unresolved Staff Comments',
    'section_two': 'Item 2 - Properties',
    'section_three': 'Item 3 - Legal Proceedings',
    'section_four': 'Item 4 - Mine Safety Disclosures',
    'section_five': 'Item 5 - Market for Registrant Common Equity',
    'section_six': 'Item 6 - Selected Financial Data',
    'section_seven': 'Item 7 - Management Discussion and Analysis',
    'section_seven_a': 'Item 7A - Quantitative and Qualitative Disclosures',
    'section_eight': 'Item 8 - Financial Statements',
}

# Standard section columns
SECTION_COLUMNS = list(SECTION_MAPPING.keys())


class TokenCounter:
    """Token counting utility."""
    
    def __init__(self, encoding_name: str = 'cl100k_base'):
        self.encoder = tiktoken.get_encoding(encoding_name)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))
    
    def encode(self, text: str) -> List[int]:
        """Encode text to tokens."""
        return self.encoder.encode(text)
    
    def decode(self, tokens: List[int]) -> str:
        """Decode tokens to text."""
        return self.encoder.decode(tokens)


class SimpleTextSplitter:
    """Simple text splitter with token-based chunking."""
    
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = TokenCounter()
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks."""
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            # Move start forward by (chunk_size - overlap)
            start += self.chunk_size - self.chunk_overlap
        
        return chunks


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)]', '', text)
    
    # Strip whitespace
    text = text.strip()
    
    return text


def get_section_name(column_name: str) -> str:
    """Get human-readable section name."""
    return SECTION_MAPPING.get(column_name, column_name)
