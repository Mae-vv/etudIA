# Backend etudIA

Ce dossier contient le code backend du projet etudIa (préparation des données Parcoursup, API d’orientation, etc.).

## Modules

- `processing.py` : fonctions de chargement et de nettoyage du jeu de données « Cartographie des formations Parcoursup ».
- `scraping.py` : contient les fonctions de récupération et de parsing des fiches formations externes.
Objectif : extraire quelques informations structurées (présentation, critères d’entrée, débouchés) pour enrichir le dataset Parcoursup.
    - fetch_page(url) : télécharge le HTML d’une fiche formation publique Parcoursup.
    - scrape_formation(url) : récupère une fiche puis renvoie un dictionnaire standardisé (presentation, criteres_entree, debouches_professionnels, frais_de_scolarite, frais_de_scolarite_boursiers, langue_options) prêt à être intégré au dataset.
    - parse_formation_page(html) renvoie un dictionnaire standardisé regroupant la
    présentation, les critères d’entrée (attendus, grille d’analyse), les débouchés, les frais
    (scolarité et candidature), les langues/options, le nombre de places, le caractère sélectif
    et le contrôle du diplôme par l’État, même si certains champs ne sont pas encore
    implémentés dans la première version.

Les fonctions de traitement des données sont testées avec pytest.
Exemple : filter_target_year est vérifiée sur un DataFrame de test pour s’assurer qu’elle ne conserve que la session cible.

## Vectorisation

### Préparation des chunks pour la base vectorielle

Avant la création de la base vectorielle, le texte `rag_document` de chaque formation est découpé en segments plus courts (“chunks”).

Cette étape est implémentée dans `src/backend/vector_store.py` :

- `chunk_rag_document(text, max_chars=2000)`  
  - découpe un `rag_document` en plusieurs segments de texte consécutifs ;  
  - la taille cible d’un chunk est de l’ordre de 1 500–2 000 caractères (≈ 500–800 tokens) ;  
  - l’objectif est d’éviter des embeddings trop longs ou hétérogènes et d’améliorer la précision de la recherche sémantique.

- `explode_chunks(df, text_col="rag_document", max_chars=2000)`  
  - transforme un DataFrame de formations (1 ligne = 1 formation) en un DataFrame de chunks ;  
  - chaque formation peut donner plusieurs lignes, une par chunk ;  
  - toutes les métadonnées de la formation (type de formation, région, apprentissage, coûts, internat, aménagements, etc.) sont recopiées sur chaque chunk ;  
  - deux colonnes supplémentaires sont ajoutées :  
    - `chunk_index` : position du chunk dans le `rag_document` (0, 1, 2, …) ;  
    - `chunk_id` : identifiant unique du chunk (par exemple combinaison de l’index de la formation et de `chunk_index`).  

Ce DataFrame “explosé” (une ligne par chunk) servira ensuite de base à la création des embeddings et à la construction de la future base vectorielle (une entrée par chunk, avec ses métadonnées).

### Base vectorielle et embeddings (v1)

Pour la première version de la base vectorielle, le projet utilise un modèle d’embedding open source de la famille multilingual‑e5 (Hugging Face, licence permissive). Ce modèle est spécialement entraîné pour la recherche sémantique multilingue et offre de bonnes performances sur le français.

Avant le choix du modèle, la longueur des chunks de ragdocument a été analysée : sur 29 026 chunks, la longueur maximale observée est d’environ 342 mots, avec une moyenne d’environ 104 mots, donc bien en‑dessous de la limite d’environ 512 tokens supportée par multilingual‑e5. Cela permet de vectoriser chaque chunk sans troncature.

Ce choix répond aussi à une contrainte de déploiement local : le modèle reste utilisable sur CPU dans un contexte étudiant, sans infrastructure GPU lourde, tout en restant cohérent avec les objectifs de souveraineté.

À plus long terme, le projet pourra évoluer vers des modèles plus lourds mais plus puissants pour la recherche sémantique, comme BGE‑M3 ou des embeddings Qwen récents, hébergés sur GPU (par exemple via un fournisseur souverain type Albert API). Ces modèles gèrent des contextes plus longs (jusqu’à plusieurs milliers de tokens), ce qui serait pertinent si la taille des documents ou le volume de données augmente.

## Base vectorielle pgvector (backend)

- SGBD : PostgreSQL lancé via Docker, administré avec pgAdmin.  
- Extension : `CREATE EXTENSION IF NOT EXISTS vector;` pour activer le type `vector` et l’opérateur `<=>` (cosinus).  
- Schéma principal : table `formations_chunks_vectors` (`chunk_id` Primary Key, métadonnées de la formation, colonne `embedding vector(768)`).
- Insertion côté Python : `src/backend/pgvector_store.py` expose `upsert_chunks(df_vs)` qui prend le DataFrame d’embeddings et fait un `INSERT ... ON CONFLICT (chunk_id) DO UPDATE`.
- Première requête RAG : un notebook encode une question lycéen en embedding, puis interroge Postgres avec `ORDER BY embedding <=> query_vector LIMIT 3` pour récupérer les chunks les plus proches.

Le notebook `13_full_vector_store.ipynb` charge le csv `parcoursup_2026_enriched_chunks.csv`,
chunk le texte avec `explode_chunks`, créé les embeddings e5 avec `build_vector_store` et insère le tout
dans la table Postgres `formations_chunks_vectors` via `upsert_chunks`

## Moteur de recommandation RAG V1

- `recommendation.py` : traduit un profil lycéen simplifié en filtres structurés (type de formation, etc.) et appelle la base pgvector pour récupérer les chunks les plus proches.
- `recommend_from_profile(profile, query_embedding)` combine filtres SQL (`WHERE ...`) et similarité cosinus (`embedding <=> query_vector`) pour renvoyer une liste de formations.
- Le notebook `12_reco_mvp.ipynb` illustre le fonctionnement sur quelques profils tests et questions en langage naturel.

### API de recommandation RAG (V1)

Le backend expose une première API HTTP pour accéder au moteur de recommandation RAG.

- **Endpoint** : `POST /recommendations`
- **Corps de requête (JSON)** :
  - `question` : texte libre de la question d’un lycéen (ex. "Je veux un BUT informatique en apprentissage en Bretagne...").
  - `profile` : objet JSON avec les contraintes structurées (ex. `typeformation`, `isapprentissage`, `maxfraisscolarite`, `region`, etc.).
  - `limit` : entier optionnel, nombre maximum de formations renvoyées (par défaut : 5).
- **Comportement** :
  - la question est encodée en embedding (modèle `intfloat/multilingual-e5-base`),
  - le profil est traduit en filtres via le moteur de recommandation (`recommend_from_profile`),
  - une requête est faite vers la base Postgres/pgvector,
  - l’API renvoie un JSON de la forme :
    ```json
    { "recommendations": [ ... ] }
    ```