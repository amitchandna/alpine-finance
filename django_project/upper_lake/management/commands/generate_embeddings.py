"""
Management command to generate embeddings for chunks.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from upper_lake.chunking.service import SIZE_CONFIG
from upper_lake.services.embedding_service import generate_embeddings
import numpy as np


class Command(BaseCommand):
    help = 'Generate embeddings for chunks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--size',
            type=str,
            default='small_384',
            choices=list(SIZE_CONFIG.keys()),
            help='Embedding size'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=32,
            help='Batch size for embedding generation'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of chunks to process'
        )
    
    def handle(self, *args, **options):
        size = options['size']
        batch_size = options['batch_size']
        limit = options['limit']
        
        config = SIZE_CONFIG[size]
        ChunkModel = config['chunk_model']
        embedding_field = f"embedding_{config['chunk_size']}" if size == 'small_384' else f"embedding_{size.split('_')[1]}"
        
        # Get chunks without embeddings
        chunks = ChunkModel.objects.filter(**{f"{embedding_field}__isnull": True})
        
        if limit:
            chunks = chunks[:limit]
        
        chunk_list = list(chunks)
        total = len(chunk_list)
        
        self.stdout.write(f"\nGenerating {size} embeddings for {total:,} chunks...")
        self.stdout.write(f"Batch size: {batch_size}\n")
        
        processed = 0
        
        for i in range(0, total, batch_size):
            batch = chunk_list[i:i + batch_size]
            texts = [chunk.text for chunk in batch]
            
            # Generate embeddings
            embeddings = generate_embeddings(texts, size=size, show_progress=False)
            
            # Update chunks
            with transaction.atomic():
                for chunk, embedding in zip(batch, embeddings):
                    setattr(chunk, embedding_field, embedding.tolist())
                    chunk.save(update_fields=[embedding_field])
            
            processed += len(batch)
            
            if processed % (batch_size * 10) == 0:
                self.stdout.write(f"Processed {processed:,}/{total:,} ({100*processed/total:.1f}%)")
        
        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Generated embeddings for {processed:,} chunks"
        ))
