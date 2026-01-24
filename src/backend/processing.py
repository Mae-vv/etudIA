import pandas as pd
from pathlib import Path

def load_parcoursup_csv(path: str | Path) -> pd.DataFrame:
    """
    Prend un chemin vers un fichier CSV Parcoursup,
    le lit avec ';' comme séparateur,
    renvoi le conenu sous forme de DataFrame pandas.
    """
    return pd.read_csv(path, sep=";", dtype=str)