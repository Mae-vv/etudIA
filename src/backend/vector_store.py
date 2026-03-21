import pandas as pd
from typing import List


def chunk_rag_document(text: str, max_chars: int = 2000) -> List[str]:
    """
    Découpe un document RAG en plusieurs segments de texte.

    Objectif
    --------
    Préparer le texte `rag_document` pour la vectorisation, en le
    découpant en "chunks" de taille raisonnable (ordre de grandeur :
    500 à 800 tokens, ~1500 à 2000 caractères) afin de :
    - éviter des embeddings trop longs ou hétérogènes ;
    - améliorer la précision de la recherche sémantique.

    Paramètres
    ----------
    text : str
        Contenu complet du `rag_document` pour une formation.
    max_chars : int
        Longueur maximale en caractères pour chaque chunk. Sert ici
        de proxy pour la longueur en tokens.

    Retour
    ------
    List[str]
        Liste de segments de texte (chunks) dérivés du document original.
    """

    if not isinstance(text, str):
        return []
    text = text.strip()
    if not text:
        return []
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]


def explode_chunks(df: pd.DataFrame,
                   text_col: str = "rag_document",
                   max_chars: int = 2000) -> pd.DataFrame:
    """
    Transforme un DataFrame de formations en DataFrame de chunks.

    Chaque ligne d'entrée (une formation) est transformée en une ou
    plusieurs lignes, une par chunk du `rag_document`. Toutes les
    métadonnées de la formation (type, région, apprentissage, coûts, etc.)
    sont recopiées sur chaque chunk.

    Paramètres
    ----------
    df : pd.DataFrame
        DataFrame enrichi contenant au moins la colonne `rag_document`.
    text_col : str
        Nom de la colonne texte à chunker.
    max_chars : int
        Longueur maximale en caractères par chunk.

    Retour
    ------
    pd.DataFrame
        DataFrame "explosé" avec :
        - une colonne `chunk_text` contenant le texte du chunk ;
        - une colonne `chunk_index` (0, 1, 2, ...) par formation ;
        - toutes les autres colonnes de métadonnées inchangées.
    """
    rows = []
    for idx, row in df.iterrows():
        chunks = chunk_rag_document(row.get(text_col, ""), max_chars=max_chars)
        for i, chunk in enumerate(chunks):
            new_row = row.copy()
            new_row["chunk_index"] = i
            new_row["chunk_text"] = chunk
            new_row["chunk_id"] = f"{idx}_{i}"
            rows.append(new_row)
    return pd.DataFrame(rows).reset_index(drop=True)
