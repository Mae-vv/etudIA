from openai import OpenAI
import numpy as np

client = OpenAI()
# Old local E5 model version (kept as reference for future self-hosted deployment)
#_model = SentenceTransformer("intfloat/multilingual-e5-base")

def get_query_embedding(question: str) -> np.ndarray:
    """
    Encode une question de lycéen en embedding normalisé pour le RAG.
    """
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=[question],
    )
    emb = resp.data[0].embedding
    return np.array(emb, dtype=float)