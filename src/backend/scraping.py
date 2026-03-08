from typing import Dict, Optional

import requests
import pandas as pd
import re 
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
    
    # Presentation
    presentation_txt = ""
    title = soup.find(
        lambda tag: tag.name == "h4"
        and "Présentation de la formation" in tag.get_text()
    )

    if title is not None:
        container = title.find_next_sibling()
        if container is not None:
            presentation_txt = container.get_text(separator="\n", strip=True)
    
    # Critères
    criteres_parts = []

    ## Nationaux
    for h4 in soup.find_all(lambda tag: tag.name == "h4" and "Les attendus nationaux" in tag.get_text()):
        bloc = h4.find_next_sibling()
        if bloc is not None:
            criteres_parts.append(bloc.get_text(separator="\n", strip=True))
    
    ## Complémentaires
    for h5 in soup.find_all(lambda tag: tag.name == "h5" and "Les attendus complémentaires" in tag.get_text()):
        bloc = h5.find_next_sibling()
        if bloc is not None:
            criteres_parts.append(bloc.get_text(separator="\n", strip=True))
    
    criteres_entree = "\n\n".join(criteres_parts)

    # Débouchés professionnels
    debouches_pro_txt = ""
    title = soup.find(lambda tag: tag.name == "h4" and "Débouchés professionnels" in tag.get_text())

    if title is not None:
        container = title.find_next_sibling()
        if container is not None:
            debouches_pro_txt = container.get_text(separator="\n", strip=True)

    # Poursuite d'études
    poursuite_etudes_txt = ""
    title = soup.find(lambda tag: tag.name == "h4" and "Poursuite d'études" in tag.get_text())

    if title is not None:
        container = title.find_next_sibling()
        if container is not None:
            poursuite_etudes_txt = container.get_text(separator="\n", strip=True)

    # Frais de scolarité
    frais_scolarite_txt = ""
    title = soup.find(lambda tag: tag.name == "h6" and "Par année" in tag.get_text())

    if title is not None:
        container = title.find_next_sibling()
        if container is not None:
            frais_scolarite_txt = container.get_text(separator="\n", strip=True)
    
    raw = frais_scolarite_txt
    if raw:
        montant = raw.split("(")[0].strip()
    else:
        montant = ""
    
    frais_scolarite_txt = montant

    # Frais de scolarité boursiers
    frais_scolarite_boursiers_txt = ""
    title = soup.find(
        lambda tag: tag.name == "h6" and "Par année pour les étudiants boursiers"
        in tag.get_text())

    if title is not None:
        container = title.find_next_sibling()
        if container is not None:
            frais_scolarite_boursiers_txt = container.get_text(separator="\n", strip=True)
    
    raw = frais_scolarite_boursiers_txt
    if raw:
        montant = raw.split("(")[0].strip()
    else:
        montant = ""
    
    frais_scolarite_boursiers_txt = montant

    # Langues options
    langue_options_txt = ""
    title = soup.find(lambda tag: tag.name == "h5"
                      and "Langues et options" in tag.get_text())
    
    if title is not None:
        container = title.find_next_sibling()
        if container is not None:
            langue_options_txt = container.get_text(separator="\n", strip=True)

    raw = langue_options_txt
    clean = "\n".join(
        line.strip()
        for line in raw.splitlines()
        if line.strip()  # on enlève les lignes vides
    )
    langue_options_txt = clean
    
    # Nombre de place
    nb_places_txt = ""
    for span in soup.find_all("span", class_="fr-badge pca-badge-custom"):
        text = span.get_text(strip=True)
        if "places" in text:
            m = re.search(r"\d+", text)
            if m:
                nb_places_txt = int(m.group(0))
            break 

    # Formation ouverte pour boursiers
    formation_ouverte_boursiers_txt = 0
    for span in soup.find_all("span", class_="fr-badge pca-badge-custom"):
        text = span.get_text(strip=True)
        if "bourses" in text.lower():
            formation_ouverte_boursiers_txt = 1
            break 

    # Diplôme contrôlé par l'Etat
    diplome_controle_etat_txt = 0
    for span in soup.find_all("span", class_="fr-badge pca-badge-custom"):
        text = span.get_text(strip=True)
        if "contrôlé" in text.lower():
            diplome_controle_etat_txt = 1
            break 

    # Formation sélective
    formation_selective_txt = 0
    for span in soup.find_all("span", class_="fr-badge pca-badge-custom"):
        text = span.get_text(strip=True)
        if "sélective" in text.lower():
            formation_selective_txt = 1
            break 

    # Epreuves de sélection
    epreuves_selection_txt = ""
    title = soup.find(lambda tag: tag.name == "h4" and
                      "Les épreuves de sélection" in tag.get_text())

    if title is not None:
        container = title.find_next_sibling()
        bloc = container.find_next("div", class_="word-break-break-word")
        if bloc is not None:
            epreuves_selection_txt = bloc.get_text(separator="\n", strip=True)

    # Frais de candidature et boursiers
    frais_candidature_txt = ""
    frais_candidature_boursiers_txt = ""
    title = soup.find(
    lambda tag: tag.name == "h4" and "Frais de candidature" in tag.get_text()
    )

    if title is not None:
        container = title.find_next("ul")
        if container is not None:
            for li in container.find_all("li"):
                text = li.get_text(strip=True)
                m = re.search(r"\d+[^\s]*\s*€", text)
                montant = m.group(0) if m else ""

                lower = text.lower()
                if "non boursiers" in lower:
                    frais_candidature_txt = montant
                elif "boursiers" in lower:
                    frais_candidature_boursiers_txt = montant

    return {
        "presentation": presentation_txt,
        "criteres_entree": criteres_entree,
        "debouches_professionnels": debouches_pro_txt,
        "poursuite_etudes": poursuite_etudes_txt,
        "frais_scolarite": frais_scolarite_txt,
        "frais_scolarite_boursiers": frais_scolarite_boursiers_txt,
        "langues_options": langue_options_txt,
        "nb_places": nb_places_txt,
        "formation_ouverte_boursiers": formation_ouverte_boursiers_txt,
        "diplome_controle_par_etat": diplome_controle_etat_txt,
        "formation_selective": formation_selective_txt,
        "epreuves_selection": epreuves_selection_txt,
        "frais_candidature": frais_candidature_txt,
        "frais_candidature_boursiers": frais_candidature_boursiers_txt,
    }

def scrape_formation(url: str) -> Dict[str, str]:
    """
    Télécharge et parse une fiche Parcoursup à partir de son URL.

    Retourne un dictionnaire standardisé avec au moins les clés :
    - presentation
    - criteres_entree
    - debouches_professionnels
    - frais_scolarite
    - frais_scolarite_boursiers
    - langues_options
    - nb_places
    - diplome_controle_par_etat
    - formation_selective
    - epreuves_selection
    - frais_candidature
    - frais_candidature_boursiers
    - poursuite_etudes
    """
    html = fetch_page(url)
    if html is None:
        return {
            "presentation": "",
            "criteres_entree": "",
            "debouches_professionnels": "",
            "poursuite_etudes": "",
            "frais_scolarite": "",
            "frais_scolarite_boursiers": "",
            "langues_options": "",
            "nb_places": "",
            "formation_ouverte_boursiers": "",
            "diplome_controle_par_etat": "",
            "formation_selective": "",
            "epreuves_selection": "",
            "frais_candidature": "",
            "frais_candidature_boursiers": "",
        }
    return parse_formation_page(html)

def enrich_with_scraping(df: pd.DataFrame, url_col: str = "link_formation") -> pd.DataFrame:
    """
    Pour chaque URL de la colonne `url_col`, appelle `fetch_page` puis
    `parse_formation_page`, et ajoute les colonnes :
    presentation, criteres_entree, debouches_professionnels,
    frais_scolarite, frais_scolarite_boursiers, langues_options,
    nb_places, diplome_controle_par_etat, formation_selective,
    epreuves_selection, frais_candidature,
    frais_candidature_boursiers, poursuite_etudes.
    """
    df = df.copy()

    for idx, url in df[url_col].head(10).items():
        if not isinstance(url, str) or not url.strip():
            continue  # on saute les URL vides
        
        infos = scrape_formation(url)

        for key, value in infos.items():
            df.loc[idx, key] = value
    
    return df