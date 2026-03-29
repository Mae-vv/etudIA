from sentence_transformers import SentenceTransformer
import numpy as np

_model = SentenceTransformer("intfloat/multilingual-e5-base")

def get_query_embedding(question: str) -> np.ndarray:
    """
    Encode une question de lycéen en embedding normalisé pour le RAG.
    """
    return _model.encode(question, normalize_embeddings=True)