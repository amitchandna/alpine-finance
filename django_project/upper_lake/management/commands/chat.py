"""
Management command for interactive chat interface.
"""

from django.core.management.base import BaseCommand
from upper_lake.services.qa_service import FinancialQAService


class Command(BaseCommand):
    help = 'Interactive chat interface for querying 10-K filings'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            default='llama3.2:1b',
            help='Ollama model to use'
        )
        parser.add_argument(
            '--size',
            type=str,
            default='small_384',
            help='Embedding size'
        )
    
    def handle(self, *args, **options):
        model = options['model']
        size = options['size']
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("Alpine Finance - Interactive Chat")
        self.stdout.write("="*60)
        self.stdout.write(f"Model: {model}")
        self.stdout.write(f"Embedding size: {size}")

        # Initialize service
        qa_service = FinancialQAService(
            ollama_model=model,
            embedding_size=size
        )
        
        self.stdout.write("Type 'exit' or 'quit' to exit\n")
        
        while True:
            try:
                question = input("You: ").strip()
                
                if question.lower() in ['exit', 'quit']:
                    self.stdout.write("\nGoodbye!")
                    break
                
                if not question:
                    continue
                
                # Get answer
                result = qa_service.ask(
                    question=question,
                    top_k=5
                )
                
                # Display answer
                self.stdout.write(f"\nAssistant: {result['answer']}\n")
                
                # Display sources
                if result['sources']:
                    self.stdout.write("\nSources:")
                    for source in result['sources']:
                        self.stdout.write(
                            f"  [{source['number']}] {source['ticker']} - "
                            f"{source['filing_date']} ({source['section']}) "
                            f"[similarity: {source['similarity']}]"
                        )
                
                # Display metadata
                meta = result['metadata']
                self.stdout.write(
                    f"\n[Chunks: {meta['num_chunks']}, "
                    f"Tokens: {meta['tokens']}, "
                    f"Avg similarity: {meta.get('avg_similarity', 0):.3f}]\n"
                )
            
            except KeyboardInterrupt:
                self.stdout.write("\n\nGoodbye!")
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"\nError: {e}\n"))
