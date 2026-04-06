from typing import Any, Dict
from fastapi import FastAPI
from pydantic import BaseModel

from src.backend.recommendation import recommend_from_profile
from src.backend.embeddings import get_query_embedding
from src.backend.profile_schema import StudentProfile
from src.backend.chat_pipeline import call_llm_advisor

app = FastAPI()

class RecommendationRequest(BaseModel):
    question: str
    profile: Dict[str, Any]
    limit: int = 5

@app.post("/recommendations")
def get_recommendations(req: RecommendationRequest):
    query_emb = get_query_embedding(req.question)
    profile: StudentProfile = req.profile
    recos = recommend_from_profile(profile, query_emb, limit=req.limit)
    return {"recommendations": recos}


class ChatRequest(BaseModel):
    message: str

@app.post("/chat-orientation")
def chat_orientation(req: ChatRequest):
    """
    Endpoint de haut niveau : reçoit un message de lycéen
    et renvoie une réponse textuelle d’orientation.
    """
    # Pour l’instant, ça lèvera encore NotImplementedError
    answer = call_llm_advisor(req.message)
    return {"answer": answer}