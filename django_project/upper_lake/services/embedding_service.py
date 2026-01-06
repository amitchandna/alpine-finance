"""
Embedding generation service using sentence-transformers.
"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

# Model configurations
MODELS = {
    'small_384': {
        'name': 'BAAI/bge-small-en-v1.5',
        'dimensions': 384
    },
    'medium_768': {
        'name': 'BAAI/bge-base-en-v1.5',
        'dimensions': 768
    },
    'large_1024': {
        'name': 'BAAI/bge-large-en-v1.5',
        'dimensions': 1024
    }
}

# Cache loaded models
_models = {}


def get_model(size: str) -> SentenceTransformer:
    """Lazy load embedding model."""
    if size not in MODELS:
        raise ValueError(f"Unknown model size: {size}. Choose from: {list(MODELS.keys())}")
    
    if size not in _models:
        model_name = MODELS[size]['name']
        print(f"Loading model: {model_name}...")
        _models[size] = SentenceTransformer(model_name)
        print(f"✓ Loaded {size}")
    
    return _models[size]


def generate_embeddings(
    texts: List[str],
    size: str = 'small_384',
    show_progress: bool = True
) -> np.ndarray:
    """
    Generate embeddings for a list of texts.
    
    Args:
        texts: List of text strings to embed
        size: Model size ('small_384', 'medium_768', 'large_1024')
        show_progress: Show progress bar
    
    Returns:
        numpy array of embeddings
    """
    if not texts:
        return np.array([])
    
    model = get_model(size)
    
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=show_progress,
        convert_to_numpy=True
    )
    
    return embeddings


def generate_query_embedding(query: str, size: str = 'small_384') -> List[float]:
    """
    Generate embedding for a single query.
    
    Args:
        query: Query text
        size: Model size
    
    Returns:
        Single embedding as list of floats
    """
    embeddings = generate_embeddings([query], size=size, show_progress=False)
    return embeddings[0].tolist()
