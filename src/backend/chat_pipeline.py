from src.backend.profile_from_text import infer_profile_from_text
from src.backend.recommendation import recommend_from_profile
from src.backend.profile_schema import StudentProfile
from sentence_transformers import SentenceTransformer
from typing import Dict, Any, List


model = SentenceTransformer("intfloat/multilingual-e5-base")

def student_orientation(message: str) -> str:
    """
    Chaîne complète :

    1. Infère un StudentProfile à partir du message.
    2. Calcule un embedding pour le RAG.
    3. Récupère des formations recommandées avec reasons/explanations.
    4. Appelle un LLM pour formuler une réponse lisible.
    """
    # 1) Profil structuré à partir du texte libre
    profile: StudentProfile = infer_profile_from_text(message)

    # 2) Embedding pour le RAG
    query_emb = model.encode(message, normalize_embeddings=True)

    # 3) Recommandations RAG
    recos: List[Dict[str, Any]] = recommend_from_profile(profile, query_emb, limit=3)

    # 4) Préparer le contexte à donner au LLM "conseiller"
    rag_context = []
    for r in recos:
        rag_context.append({
            "type_formation": r["type_formation"],
            "commune": r["commune"],
            "frais_scolarite": r["frais_scolarite"],
            "distance": r["distance"],
            "explanation": r.get("explanation"),
        })

    # 5) Appel au LLM 2 (pseudo-code)
    # answer = call_llm_conseiller(message, profile, rag_context)
    # return answer

    raise NotImplementedError("Chaîne complète sans LLM conseiller pour le moment.")

def call_llm_advisor(
    message: str,
    profile: StudentProfile,
    rag_context: List[Dict[str, Any]],
) -> str:
    """
    Utilise un LLM pour générer une réponse d'orientation à partir :
    - du message brut du lycéen,
    - du profil structuré StudentProfile,
    - des formations proposées par le RAG avec leurs explications.
    """
    # 1) Construire un system prompt qui cadre le rôle (orientation, neutralité, RGPD)
    # 2) Construire un message "assistant caché" qui résume profile + rag_context
    # 3) Appeler le LLM (pseudo-code) et renvoyer le texte
    raise NotImplementedError("LLM conseiller non implémenté.")