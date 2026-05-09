import json
from openai import OpenAI
from typing import Dict, Any, List

from src.backend.profile_schema import StudentProfile
from src.backend.profile_from_text import infer_profile_from_text
from src.backend.recommendation import recommend_from_profile
from src.backend.embeddings import get_query_embedding

# Old local E5 model version (kept as reference for future self-hosted deployment)
# model = SentenceTransformer("intfloat/multilingual-e5-base")
client = OpenAI()

def format_history_for_llm(history: List[Dict[str, Any]]) -> str:
  """
  Transforme les 4 derniers messages en texte lisible pour le LLM.
  """
  lines: List[str] = []
  for m in history:
      role = m.role
      content = m.content or ""
      if not content.strip():
          continue
      prefix = "Lycéen" if role == "user" else "Assistant"
      lines.append(f"{prefix} : {content}")
  return "\n".join(lines)

def student_orientation(message: str, history: List[Dict[str, Any]]) -> str:
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
    # Old way query_emb = model.encode(message, normalize_embeddings=True)
    query_emb = get_query_embedding(message)

    # 3) Recommandations RAG
    recos: List[Dict[str, Any]] = recommend_from_profile(profile, query_emb, limit=3)

    # 4) Préparer le contexte à donner au LLM "conseiller"
    rag_context: List[Dict[str, Any]] = []
    for r in recos:
        text = r.get("chunk_text") or ""
        short_text = text[:500]

        rag_context.append({
            "type_formation": r["type_formation"],
            "commune": r["commune"],
            "frais_scolarite": r["frais_scolarite"],
            "explanation": r.get("explanation"),
            "content": short_text,
        })

    # 5) Historique récent mis en forme pour le LLM
    history_text = format_history_for_llm(history)

    # 6) Appel au LLM conseiller
    answer = call_llm_advisor(
        message,
        profile,
        rag_context,
        history_text,
    )

    return answer

def call_llm_advisor(
    message: str,
    profile: StudentProfile,
    rag_context: List[Dict[str, Any]],
    history_text: str,
) -> str:
    """
    Utilise gpt-4o-mini pour générer une réponse d'orientation à partir :
    - du message brut du lycéen,
    - du profil structuré StudentProfile,
    - des formations proposées par le RAG avec leurs explications.
    """
    system_prompt = (
        "Tu es un assistant d'orientation pour lycéens.\n"
        "Tu t'appuies UNIQUEMENT sur le profil structuré de l'élève, "
        "l'historique récent du chat et les formations fournies dans le contexte JSON.\n"
        "Tu ne dois JAMAIS inventer de formation, de ville ou de détail qui n'y figure pas.\n"
        "Tu restes neutre et tu n'infères jamais l'origine, le genre, "
        "la personnalité ou le niveau social.\n"
        "\n"
        "L'historique du chat contient les précisions et éventuels changements d'avis "
        "de l'élève (par exemple : d'abord la santé, puis l'envie d'ajouter "
        "l'informatique). Tu dois chercher à COMBINER ces intérêts autant que possible, "
        "et non à remplacer le premier par le dernier.\n"
        "Prends aussi en compte son rythme de vie et ses contraintes éventuelles "
        "(par exemple pratique sportive intensive, préférence pour le matin, budget, etc.) "
        "lorsque tu expliques pourquoi une formation peut lui convenir.\n"
        "Si aucune formation ne combine clairement tous les intérêts ou contraintes, "
        "explique-le honnêtement et précise en quoi chaque formation répond seulement "
        "à une partie de la demande.\n"
        "\n"
        "Lorsque plusieurs formations sont pertinentes, privilégie les formations publiques "
        "ou à frais de scolarité modérés, sauf si le contexte indique explicitement "
        "qu'un établissement privé est recherché.\n"
        "\n"
        "Tu peux citer au maximum 3 formations différentes.\n"
        "Pour chaque formation que tu cites :\n"
        "- résume en 1 à 2 phrases ce qu'on y apprend et les compétences développées ;\n"
        "- explique pourquoi elle correspond au profil et aux échanges récents "
        "(matières aimées ou difficiles, centres d'intérêt, souhait d'apprentissage, "
        "contraintes éventuelles, rythme de vie) en t'appuyant sur le champ 'explanation' fourni ;\n"
        "- ne parle pas de critères (comme les frais, la sélectivité, la distance) "
        "s'ils ne sont pas mentionnés dans le contexte ou l'explication.\n"
        "\n"
        "Si une formation répond surtout à un seul des centres d'intérêt "
        "(par exemple surtout santé ou surtout informatique), dis-le clairement "
        "et compare-la rapidement aux autres.\n"
        "Conclue en une phrase simple pour rappeler que ce sont des pistes à explorer "
        "et qu'il peut en parler avec un conseiller d'orientation ou un adulte de confiance.\n"
    )

    # Résumé du profil et des recos pour le modèle
    profile_json = json.dumps(profile, ensure_ascii=False)
    rag_json = json.dumps(rag_context, ensure_ascii=False, default=str)

    context_parts = []
    if history_text.strip():
        context_parts.append(
            "Historique récent du chat (du plus ancien au plus récent) :\n"
            + history_text
        )
    context_parts.append(
        "Voici le profil structuré du lycéen (StudentProfile) :\n"
        f"{profile_json}"
    )
    context_parts.append(
        "Voici une liste de formations proposées par un moteur RAG, "
        "avec une explication pour chacune :\n"
        f"{rag_json}"
    )
    context_parts.append(
        "En t'appuyant uniquement sur ces éléments, rédige une réponse pour le lycéen."
    )

    context_message = "\n\n".join(context_parts)

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": context_message},
            {"role": "user", "content": message},
        ],
        max_output_tokens=600,  # contrôle du coût
    )

    answer = response.output[0].content[0].text
    return answer