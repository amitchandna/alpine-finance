"""
Database models for Alpine Finance RAG system.
"""

from django.db import models
from pgvector.django import VectorField



class TenKData(models.Model):
    """Raw 10-K filing data (your existing table)"""
    
    id = models.AutoField(primary_key=True)
    ticker = models.TextField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    
    # Section columns (adjust based on your actual schema)
    section_one = models.TextField(null=True, blank=True)
    section_one_a = models.TextField(null=True, blank=True)
    section_one_b = models.TextField(null=True, blank=True)
    section_seven = models.TextField(null=True, blank=True)
    section_seven_a = models.TextField(null=True, blank=True)
    # Add other section columns as needed
    
    class Meta:
        db_table = "raw_ten_k_data"
        managed = False  # Don't let Django manage this table


# Small Embeddings (384 dimensions)
class RAGFilingSectionSmall(models.Model):
    """Filing sections for small embeddings (384-dim)"""
    
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
    """Text chunks for small embeddings (384-dim)"""
    
    id = models.AutoField(primary_key=True)
    section = models.ForeignKey(
        RAGFilingSectionSmall,
        on_delete=models.CASCADE,
        related_name='chunks',
        db_column='section_id'
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


# Medium Embeddings (768 dimensions)
class RAGFilingSectionMedium(models.Model):
    """Filing sections for medium embeddings (768-dim)"""
    
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
        db_table = "rag_filing_sections_medium"
        indexes = [
            models.Index(fields=["ticker", "filing_type", "section_name"]),
        ]


class RAGChunkMedium(models.Model):
    """Text chunks for medium embeddings (768-dim)"""
    
    id = models.AutoField(primary_key=True)
    section = models.ForeignKey(
        RAGFilingSectionMedium,
        on_delete=models.CASCADE,
        related_name='chunks',
        db_column='section_id'
    )
    chunk_index = models.IntegerField()
    text = models.TextField()
    token_count = models.IntegerField()
    embedding_768 = VectorField(dimensions=768, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rag_chunks_medium"
        indexes = [
            models.Index(fields=["section", "chunk_index"]),
        ]


# Large Embeddings (1024 dimensions)
class RAGFilingSectionLarge(models.Model):
    """Filing sections for large embeddings (1024-dim)"""
    
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
        db_table = "rag_filing_sections_large"
        indexes = [
            models.Index(fields=["ticker", "filing_type", "section_name"]),
        ]


class RAGChunkLarge(models.Model):
    """Text chunks for large embeddings (1024-dim)"""
    
    id = models.AutoField(primary_key=True)
    section = models.ForeignKey(
        RAGFilingSectionLarge,
        on_delete=models.CASCADE,
        related_name='chunks',
        db_column='section_id'
    )
    chunk_index = models.IntegerField()
    text = models.TextField()
    token_count = models.IntegerField()
    embedding_1024 = VectorField(dimensions=1024, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rag_chunks_large"
        indexes = [
            models.Index(fields=["section", "chunk_index"]),
        ]
