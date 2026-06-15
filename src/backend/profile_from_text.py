from src.backend.profile_schema import StudentProfile
from openai import OpenAI
import json

client = OpenAI()

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

    Utilise un LLM (gpt-5-nano car bon pour les tâches de
    classification/résumé/tâches d'extraction...)
    pour analyser un message libre d'un lycéen
    et renvoyer un StudentProfile JSON.
    """

    system = (
        "Tu es un assistant qui analyse des messages de lycéens pour "
        "remplir un profil structuré StudentProfile. "
        "Tu ne fais PAS de psychologie, tu ne déduis PAS l'origine, "
        "le genre ou la personnalité. "
        "Tu dois renvoyer UNIQUEMENT un objet JSON avec les clés : "
        "type_formation, is_apprentissage, max_frais_scolarite, commune, "
        "domains_interet, matieres_aimees, matieres_evitees, "
        "preference_rythme, preference_travail, niveau_idee_orientation. "
        "Les champs peuvent être null ou des listes vides si l'information "
        "n'est pas présente dans le message."
    )

    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ],
        max_output_tokens=300,
        reasoning={"effort": "minimal"},
        text={"format": {"type": "json_object"}},
    )

    # Cherche le bloc "message" dynamiquement (ignore le bloc "reasoning")
    message_block = next(
        (item for item in response.output if item.type == "message"), None
    )

    if not message_block:
        raise ValueError(f"No message block in LLM response. output={response.output}")

    raw = message_block.content[0].text

    data = json.loads(raw)

    return data