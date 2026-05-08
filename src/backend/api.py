from typing import Any, Dict, List, Optional
from fastapi import FastAPI
from pydantic import BaseModel

from src.backend.recommendation import recommend_from_profile
from src.backend.embeddings import get_query_embedding
from src.backend.profile_schema import StudentProfile
from src.backend.chat_pipeline import student_orientation

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

class ChatMessage(BaseModel):
    role: str 
    content: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

@app.post("/chat-orientation")
def chat_orientation(req: ChatRequest):
    """
    Endpoint de haut niveau : reçoit un message de lycéen
    et renvoie une réponse textuelle d’orientation.
    """
    answer = student_orientation(req.message, req.history)
    return {"answer": answer}

import os
from src.backend.pgvector_store import get_pg_connection

@app.get("/debug-db-url")
def debug_db_url():
    return {"DATABASE_URL": os.getenv("DATABASE_URL")}

@app.get("/health-db")
def health_db():
    try:
        conn = get_pg_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()
        return {"db": "ok"}
    except Exception as e:
        return {"db": "error", "detail": str(e)}