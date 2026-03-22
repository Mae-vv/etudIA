import os
import psycopg2
from psycopg2.extras import execute_values
import numpy as np
import pandas as pd
from dotenv import load_dotenv

# Charger les variables d'environnement (si ce n'est pas déjà fait)
load_dotenv()

def get_pg_connection():
    """
    Ouvre une connexion à la base PostgreSQL etudIA (docker pgvector).

    Les paramètres de connexion sont lus dans le .env :
    PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD.

    Retourne :
        psycopg2.extensions.connection : objet connexion à utiliser avec cursor().
    """
    conn = psycopg2.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
    )
    return conn

def clean_frais(value):
    if pd.isna(value):
        return None
    if isinstance(value, str):
        # Extraire nombre : "178 euros" → 178
        import re
        m = re.search(r'(\d+(?:,\d+)?)', str(value))
        return int(m.group(1).replace(',', '.')) if m else None
    return int(value)

def upsert_chunks(df_vs: pd.DataFrame) -> None:
    """
    Insère ou met à jour les chunks et leurs embeddings
    dans la table formations_chunks_vectors.

    df_vs doit contenir au moins les colonnes :
    chunk_id, chunk_index, chunk_text,
    type_formation, type_etablissement, commune,
    is_apprentissage, frais_scolarite,
    formation_selective, formation_ouverte_boursiers,
    embedding (vecteur numpy/list de longueur 768).
    """
    conn = get_pg_connection()
    cur = conn.cursor()

    rows = []
    for _, row in df_vs.iterrows():
        emb = row["embedding"]

        # S'assurer que c'est une liste de float (pgvector attend un array)
        if isinstance(emb, np.ndarray):
            emb = emb.tolist()

        rows.append((
            row["chunk_id"],
            int(row["chunk_index"]),
            row["chunk_text"],
            row["type_formation"],
            row["type_etablissement"],
            row["commune"],
            bool(row["is_apprentissage"]),
            clean_frais(row["frais_scolarite"]),
            bool(row["formation_selective"]),
            bool(row["formation_ouverte_boursiers"]),
            emb,
        ))

    execute_values(
        cur,
        """
        INSERT INTO formations_chunks_vectors
        (chunk_id, chunk_index, chunk_text,
         type_formation, type_etablissement, commune,
         is_apprentissage, frais_scolarite,
         formation_selective, formation_ouverte_boursiers,
         embedding)
        VALUES %s
        ON CONFLICT (chunk_id) DO UPDATE
        SET embedding = EXCLUDED.embedding
        """,
        rows,
    )

    conn.commit()
    cur.close()
    conn.close()