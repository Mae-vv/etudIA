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
    'code_formation',
    'Code interne Parcoursup de la formation',
    'Code interne Parcoursup pour les portails'
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

def filter_target_year(df: pd.DataFrame, year: str) -> pd.DataFrame:
    """
    Filtrer les lignes du DataFrame sur l'année donnée
    pour se concentrer sur l'offre de formation de la campagne cible.
    """
    return df[df["session"] == year]

def add_is_apprentissage(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute une colonne binaire 'is_apprentissage' :
    1 si la formation est en apprentissage, 0 sinon.
    """
    df = df.copy()
    df["is_apprentissage"] = (df["apprentissage"] == "Formations en apprentissage").astype(int)
    return df

def add_internat_code(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute une colonne 'internat_code' :
    0 = pas d'internat connu
    1 = internat pour filles et garçons
    2 = internat réservé aux filles
    3 = internat réservé aux garçons
    """
    df = df.copy()
    df["internat_code"] = 0  # valeur par défaut
    df.loc[df["internat"] == "Etablissements avec internat pour filles et garçons", "internat_code"] = 1
    df.loc[df["internat"] == "Etablissements avec internat pour filles", "internat_code"] = 2
    df.loc[df["internat"] == "Etablissements avec internat pour garçons", "internat_code"] = 3
    return df

def clean_parcoursup_data(path: str | Path, year: str) -> pd.DataFrame:
    """
    Lance le pipeline complet de nettoyage pour le fichier Parcoursup:
    chargement, suppression des colonnes inutiles, renommage
    et filtrage sur l'année cible.
    """
    df = load_parcoursup_csv(path)
    df = drop_unused_columns(df)
    df = rename_columns(df)
    df = filter_target_year(df, year)
    df = add_is_apprentissage(df)
    df = add_internat_code(df)
    return df
