import pandas as pd
from pathlib import Path

UNUSED_COLUMNS = [
    'Localisation',
    'etablissement_id_paysage',
    'composante_id_paysage',
    'rnd',
    "Lien vers les données statistiques pour l'année antérieure",
    'code interne parcoursup de la formation',
    'code interne parcoursup pour les portails',
    'code_formation'
]

RENAMING_MAP = {
    "Session": "session",
    "Identifiant de l'établissement": "id_etablissement",
    "Nom de l'établissement": "name_etablissement",
    "Types d'établissement": "type_etablissement",
    "Types de formation": "type_formation",
    "Nom long de la formation": "name_formation",
    "Mentions/Spécialités": "mentions_specialites",
    "Formations en apprentissage": "apprentissage",
    "Internat": "internat",
    "Aménagement": "amenagement",
    "informations complémentaires": "info_complementaires",
    "Région": "region",
    "Département": "departement",
    "Commune": "commune",
    "Lien vers la fiche formation": "link_formation",
    "Site internet de l'établissement": "website_etablissement",
    "Nom court de la formation": "short_name_formation",
}

def load_parcoursup_csv(path: str | Path) -> pd.DataFrame:
    """
    Prend un chemin vers un fichier CSV Parcoursup,
    le lit avec ';' comme séparateur,
    renvoi le conenu sous forme de DataFrame pandas.
    """
    return pd.read_csv(path, sep=";", dtype=str)

def drop_unused_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supprime les colonnes du DataFrame les colonnes non nécessaires
    pour l'analyse Parcoursup dans etudIA.
    """
    return df.drop(columns=[col for col in UNUSED_COLUMNS if col in df.columns])

def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renomme les colonnes du DataFrame selon RENAMING_MAP
    pour plus de lisibilité et de cohérence.
    """
    return df.rename(columns=RENAMING_MAP)

def filter_target_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtrer les lignes du DataFrame sur l'année 2026
    pour se concentrer sur l'offre de formation actuelle.
    """
    return df[df["session"] == "2026"]