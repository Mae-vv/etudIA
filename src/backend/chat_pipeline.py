import json
from openai import OpenAI
from typing import Dict, Any, List
from sentence_transformers import SentenceTransformer

from src.backend.profile_schema import StudentProfile
from src.backend.profile_from_text import infer_profile_from_text
from src.backend.recommendation import recommend_from_profile

model = SentenceTransformer("intfloat/multilingual-e5-base")
client = OpenAI()

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

    # 5) Appel au LLM 2
    answer = call_llm_advisor(message, profile, rag_context)

    return answer

def call_llm_advisor(
    message: str,
    profile: StudentProfile,
    rag_context: List[Dict[str, Any]],
) -> str:
    """
    Utilise gpt-4o-mini pour générer une réponse d'orientation à partir :
    - du message brut du lycéen,
    - du profil structuré StudentProfile,
    - des formations proposées par le RAG avec leurs explications.
    """
    system_prompt = (
        "Tu es un assistant d'orientation pour lycéens.\n"
        "Tu t'appuies UNIQUEMENT sur les formations fournies dans le contexte.\n"
        "Tu restes neutre, tu n'infères jamais l'origine, le genre, "
        "la personnalité ou le niveau social.\n"
        "Tu expliques clairement tes suggestions et rappelles que ce sont "
        "des pistes, pas des décisions définitives.\n"
        "Pour chaque formation que tu cites, explique en une phrase pourquoi elle correspond, "
        "en t'appuyant uniquement sur le champ 'explanation' fourni.\n"
        "Ne parle pas de critères (par exemple les frais) s'ils ne sont pas mentionnés dans "
        "le profil structuré ou dans 'explanation'.\n"
    )

    # Résumé du profil et des recos pour le modèle
    profile_json = json.dumps(profile, ensure_ascii=False)
    rag_json = json.dumps(rag_context, ensure_ascii=False)

    context_message = (
        "Voici le profil structuré du lycéen (StudentProfile) :\n"
        f"{profile_json}\n\n"
        "Voici une liste de formations proposées par un moteur RAG, "
        "avec une explication pour chacune :\n"
        f"{rag_json}\n\n"
        "En t'appuyant uniquement sur ces éléments, rédige une réponse pour le lycéen."
    )

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": context_message},
            {"role": "user", "content": message},
        ],
        max_output_tokens=300,  # contrôle du coût
    )

    answer = response.output[0].content[0].text
    return answer