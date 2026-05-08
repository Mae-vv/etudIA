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
    db_url = os.getenv("DATABASE_URL")

    if db_url:
        return psycopg2.connect(db_url)

    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
    )


import re
def clean_frais(value):
    if pd.isna(value):
        return None
    s = str(value)
    m = re.search(r'(\d+(?:[.,]\d+)?)', s)
    if not m:
        return None
    num = float(m.group(1).replace(',', '.'))
    return int(round(num))

def upsert_chunks(df_vs, batch_size: int = 1000) -> None:
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

    print("Début upsert_chunks, nb lignes:", len(df_vs))

    rows_batch = []
    total = 0

    for _, row in df_vs.iterrows():
        emb = row["embedding"]

        # S'assurer que c'est une liste de float (pgvector attend un array)
        if isinstance(emb, np.ndarray):
            emb = emb.tolist()

        rows_batch.append((
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

        if len(rows_batch) >= batch_size:
            print("Envoi d'un batch de", len(rows_batch))
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
                rows_batch,
            )
            conn.commit()
            total += len(rows_batch)
            rows_batch = []

    if rows_batch:
        print("Envoi dernier batch de", len(rows_batch))
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
            rows_batch,
        )

    conn.commit()
    total += len(rows_batch)

    print(f"Upsert terminé, {total} lignes traitées.")
    cur.close()
    conn.close()