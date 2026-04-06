from src.backend.profile_schema import StudentProfile

def infer_profile_from_text(message: str) -> StudentProfile:
    """
    Analyse un message libre d'un lycéen et en déduit un StudentProfile.

    Exemple de message :

    "J'aime le sport, les maths et pas l'histoire-géo. Je fais du tennis en club
    et l'été j'aime faire du kayak. Je suis un lève-tôt et j'aime travailler en
    équipe. Je n'ai aucune idée vers quoi me diriger comme filière, pourrais-tu
    m'orienter ?"

    Exemple de profil structuré attendu (tous les champs sont optionnels) :

    {
        "type_formation": null,
        "is_apprentissage": null,
        "max_frais_scolarite": null,
        "commune": null,
        "domains_interet": ["sport", "maths"],
        "matieres_aimees": ["maths"],
        "matieres_evitees": ["histoire-géo"],
        "preference_rythme": "matin",
        "preference_travail": "équipe",
        "niveau_idee_orientation": "aucune_idee"
    }

    Cette fonction sera plus tard implémentée à l'aide d'un LLM qui doit
    toujours renvoyer un objet JSON compatible avec StudentProfile.
    Pour l'instant, elle peut lever NotImplementedError.
    """
    raise NotImplementedError("LLM-based profile inference not implemented yet.")