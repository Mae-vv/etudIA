from typing import Any, Dict
from fastapi import FastAPI
from pydantic import BaseModel

from src.backend.recommendation import recommend_from_profile
from src.backend.embeddings import get_query_embedding

app = FastAPI()

class RecommendationRequest(BaseModel):
    question: str
    profile: Dict[str, Any]
    limit: int = 5

@app.post("/recommendations")
def get_recommendations(req: RecommendationRequest):
    query_emb = get_query_embedding(req.question)
    recos = recommend_from_profile(req.profile, query_emb, limit=req.limit)
    return {"recommendations": recos}