from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup

def fetch_page(url: str, timeout: int = 10) -> Optional[str]:
    """
    Récupère le contenu HTML brut d'une page externe.

    Paramètres
    ----------
    url : str
        URL de la page à récupérer.
    timeout : int
        Temps maximum (en secondes) avant d'abandonner la requête.

    Retour
    ------
    html : str ou None
        Contenu HTML de la page si la requête a réussi, None sinon.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        # Plus tard : logger l'erreur
        return None


def parse_formation_page(html: str) -> Dict[str, str]:
    """
    Extrait des informations clés depuis une fiche formation Parcoursup.

    Clés retournées (quand l'information est trouvée) :
    - 'presentation' : texte qui décrit la formation, son contenu et ses objectifs.
    - 'criteres_entree' : texte qui explique comment les candidatures sont analysées
      (attendus nationaux et complémentaire).
    - 'debouches_professionnels' : texte qui présente les métiers et secteurs accessibles
      après la formation.
    - 'frais_de_scolarite' : texte qui énonce le coût de la formation.
    - 'frais_de_scolarite_boursiers' : texte qui énonce le coût de la formation pour les
      étudiants boursiers.
    - 'langue_options' : texte qui présente les langues et options.
    - 'nb_places': nombre de places disponibles.
    - 'diplome_controle_par_etat': vérifier si formation reconnue par l'Etat.
    - 'formation_selective': formation sélective ou non.
    - 'epreuves_selection': les épreuves de sélections.
    - 'frais_candidature': frais de candidature pour les étudiants.
    - 'frais_candidature_boursiers': frais de candidature à la formation pour les
        étudiants boursiers
    - 'poursuite_etudes': possibilité de poursuite d'études.

    Paramètres
    ----------
    html : str
        Contenu HTML de la fiche formation.

    Retour
    ------
    infos : dict
        Dictionnaire avec les clés ci-dessus. Les valeurs peuvent être des chaînes vides
        si l'information n'a pas été trouvée.
    """
    soup = BeautifulSoup(html, "html.parser")
    
    presentation_txt = ""
    title = soup.find(
        lambda tag: tag.name == "h4"
        and "Présentation de la formation" in tag.get_text()
    )

    if title is not None:
        container = title.find_next_sibling()
        if container is not None:
            presentation_txt = container.get_text(separator="\n", strip=True)

    return {
        "presentation": presentation_txt,
        "criteres_entree": "",
        "debouches_professionnels": "",
        "frais_scolarite": "",
        "frais_scolarite_boursiers": "",
        "langues_options": "",
        "nb_places": "",
        "diplome_controle_par_etat": "",
        "formation_selective": "",
        "epreuves_selection": "",
        "frais_candidature": "",
        "frais_candidature_boursiers": "",
        "poursuite_etudes": "",
    }

def scrape_formation(url: str) -> Dict[str, str]:
    """
    Récupère et parse une fiche formation Parcoursup à partir de son URL.

    Retourne un dictionnaire avec au moins les clés :
    - 'presentation'
    - 'criteres_entree'
    - 'debouches_professionnels'
    - 'frais_de_scolarite'
    - 'frais_de_scolarite_boursiers'
    - 'langue_options'
    """
    html = fetch_page(url)
    if html is None:
        return {
            "presentation": "",
            "criteres_entree": "",
            "debouches_professionnels": "",
            "frais_de_scolarite": "",
            "frais_de_scolarite_boursiers": "",
            "langue_options": ""
        }
    return parse_formation_page(html)