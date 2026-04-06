from typing import Any, Dict, List, Optional, TypedDict

class StudentProfile(TypedDict, total=False):
    # Bloc 1 : contraintes objectives
    type_formation: Optional[str]
    is_apprentissage: Optional[bool]
    max_frais_scolarite: Optional[int]
    commune: Optional[str]

    # Bloc 2 : centres d’intérêt & matières
    domains_interet: List[str]
    matieres_aimees: List[str]
    matieres_evitees: List[str]

    # Bloc 3 : style de travail / rythme
    preference_rythme: Optional[str]        # "matin", "après-midi", "indifférent"
    preference_travail: Optional[str]       # "équipe", "solo", "mixte"
    niveau_idee_orientation: Optional[str]  # "aucune idee", "quelques pistes", "assez clair"