from typing import Dict, Any, List
import numpy as np
from src.backend.pgvector_store import get_pg_connection
from src.backend.profile_schema import StudentProfile

def build_filters_from_profile(profile: StudentProfile) -> Dict[str, Any]:
    """
    Traduit un 'profil lycéen' simplifié en filtres structurés.

    Exemple de profil (pour l'instant) :
      {
        "type_formation": "BUT",
        "is_apprentissage": True,
        "max_frais_scolarite": 1500,
        "region": "Bretagne"
      }

    Retourne un dict avec les contraintes à appliquer dans le WHERE SQL.
    """
    filters: Dict[str, Any] = {}

    type_formation = profile.get("type_formation")
    if type_formation is not None:
        filters["type_formation"] = type_formation
    
    is_apprentissage = profile.get("is_apprentissage")
    if is_apprentissage is not None:
        filters["is_apprentissage"] = is_apprentissage
    
    max_frais = profile.get("max_frais_scolarite")
    if max_frais is not None:
        filters["max_frais_scolarite"] = max_frais
    
    commune = profile.get("commune")
    if commune is not None:
        filters["commune"] = commune

    return filters

def recommend_from_profile(profile: StudentProfile,
                           query_embedding: np.ndarray,
                           limit: int = 5) -> List[Dict[str, Any]]:
    """
    Applique les filtres + la similarité RAG dans Postgres et renvoie
    une liste de recommandations (formations) pour ce profil.
    """
    filters = build_filters_from_profile(profile)
    
    where_clauses = []
    params: List[Any] = []

    if "type_formation" in filters:
        where_clauses.append("type_formation ILIKE %s")
        params.append(f"%{filters['type_formation']}%")

    if "is_apprentissage" in filters:
        where_clauses.append("is_apprentissage = %s")
        params.append(filters["is_apprentissage"])
    
    if "max_frais_scolarite" in filters:
        where_clauses.append("(frais_scolarite <= %s OR frais_scolarite IS NULL)")
        params.append(filters["max_frais_scolarite"])
    
    if "commune" in filters:
        where_clauses.append("commune = %s")
        params.append(filters["commune"])

    where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"

    conn = get_pg_connection()
    cur = conn.cursor()

    sql = f"""
        SELECT
            chunk_id,
            chunk_text,
            type_formation,
            commune,
            frais_scolarite,
            embedding <=> (%s::vector) AS distance
        FROM formations_chunks_vectors
        WHERE {where_sql}
        ORDER BY embedding <=> (%s::vector)
        LIMIT %s;
    """

    # Valeurs des params
    params_full = [query_embedding.tolist()] + params + [query_embedding.tolist(), limit]

    cur.execute(sql, params_full)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    results: List[Dict[str, Any]] = []
    for row in rows:

        reason = {
            "match_type_formation": (
                profile.get("type_formation") is None
                or row[2] is None
                or profile.get("type_formation") in row[2]
            ),
            "match_apprentissage": (
                profile.get("is_apprentissage") is None
                or filters.get("is_apprentissage") is None
                or filters.get("is_apprentissage") == profile.get("is_apprentissage")
            ),
            "under_budget": (
                profile.get("max_frais_scolarite") is None
                or row[4] is None
                or row[4] <= profile["max_frais_scolarite"]
            ),
        }

        explanation_parts = []
        if reason["match_type_formation"]:
            explanation_parts.append("correspond au type de formation que tu recherches")
        if reason["match_apprentissage"]:
            explanation_parts.append("propose de l'apprentissage, comme tu le souhaites")
        if reason["under_budget"]:
            explanation_parts.append("respecte ton budget (ou ne dépasse pas le plafond indiqué)")

        explanation = " ; ".join(explanation_parts) if explanation_parts else "formation proche de ta demande."

        results.append({
            "chunk_id": row[0],
            "chunk_text": row[1],
            "type_formation": row[2],
            "commune": row[3],
            "frais_scolarite": row[4],
            "distance": row[5],
            "reason": reason,
            "explanation": explanation,
        })
    return results
