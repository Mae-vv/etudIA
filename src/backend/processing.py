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