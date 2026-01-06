"""
Management command to chunk 10-K filings.
"""

from django.core.management.base import BaseCommand
from upper_lake.models import TenKData
from upper_lake.chunking.service import TenKChunker, SIZE_CONFIG


class Command(BaseCommand):
    help = 'Chunk 10-K filings into RAG tables'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--size',
            type=str,
            default='small_384',
            choices=list(SIZE_CONFIG.keys()) + ['all'],
            help='Embedding size to use'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of filings to process'
        )
        parser.add_argument(
            '--start-id',
            type=int,
            default=1,
            help='Start from specific filing ID'
        )
    
    def handle(self, *args, **options):
        size = options['size']
        limit = options['limit']
        start_id = options['start_id']
        
        # Get filing IDs
        filings = TenKData.objects.filter(id__gte=start_id).order_by('id')
        
        if limit:
            filings = filings[:limit]
        
        filing_ids = list(filings.values_list('id', flat=True))
        
        self.stdout.write(f"\nProcessing {len(filing_ids)} filings...")
        
        # Process for each size
        sizes_to_process = list(SIZE_CONFIG.keys()) if size == 'all' else [size]
        
        for s in sizes_to_process:
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"Processing size: {s}")
            self.stdout.write(f"{'='*60}\n")
            
            chunker = TenKChunker(size=s)
            result = chunker.chunk_batch(filing_ids)
            
            self.stdout.write(self.style.SUCCESS(
                f"\n✓ Completed {s}:\n"
                f"  Sections: {result['total_sections']}\n"
                f"  Chunks: {result['total_chunks']}\n"
                f"  Tokens: {result['total_tokens']:,}\n"
                f"  Failures: {len(result['failures'])}\n"
            ))
            
            if result['failures']:
                self.stdout.write(self.style.WARNING(
                    f"\nFailed filings: {result['failures'][:5]}"
                ))
