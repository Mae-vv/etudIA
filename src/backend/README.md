# Backend etudIA
Ce dossier contient le code backend du projet etudIA : préparation des données Parcoursup, moteur de recommandation RAG, API d’orientation et intégration avec le front Next.js.

## Modules principaux
- `processing.py` : Fonctions de chargement et de nettoyage du jeu de données « Cartographie des formations Parcoursup » (suppression de colonnes inutiles, renommage, filtrage par année, création de variables dérivées comme is_apprentissage, codes d’internat, aménagements, etc.).

- `scraping.py` :
Fonctions de récupération et de parsing des fiches formations externes (pages publiques Parcoursup) pour enrichir le dataset avec des champs textuels supplémentaires.

  - `fetch_page(url)` : télécharge le HTML d’une fiche formation.
  - `parse_formation_page(html)` : extrait un dictionnaire standardisé avec présentation, critères d’entrée, débouchés, poursuite d’études, frais de scolarité (boursiers / non boursiers), langues/options, nombre de places, caractère sélectif, contrôle du diplôme par l’État, etc.
  - `scrape_formation(url)` : enchaîne téléchargement + parsing pour renvoyer un dictionnaire prêt à être fusionné avec le dataset Parcoursup.
  - `enrich_with_scraping(df, ...)` : applique scrape_formation sur un DataFrame de formations pour ajouter ces colonnes.

Les fonctions de traitement des données sont testées avec pytest (par exemple, filter_target_year est vérifiée sur un DataFrame de test pour garantir qu’elle ne conserve que la session cible).

## Vectorisation et préparation RAG

### Données Parcoursup et préparation RAG

Les jeux de données d’entrée, le pipeline de nettoyage et la préparation de `rag_document`
sont documentés dans `src/data/README.md`.

La base pgvector utilisée par le backend est construite à partir de :
- `parcoursup_2026_enriched_rag.csv`
- `parcoursup_2026_enriched_chunks.csv`

### Chunking des documents

Avant la création de la base vectorielle, le texte `rag_document` de chaque formation est découpé en segments (“chunks”) plus courts.

Ce comportement est implémenté dans `src/backend/vector_store.py` :
- `chunk_rag_document(text, max_chars=2000)`

   - découpe le texte en segments consécutifs d’environ 1 500–2 000 caractères (≈ 500–800 tokens) ;
   - objectif : éviter des embeddings trop longs ou hétérogènes, et améliorer la précision de la recherche sémantique.

- `explode_chunks(df, text_col="rag_document", max_chars=2000)`

  - transforme un DataFrame de formations (1 ligne = 1 formation) en un DataFrame de chunks (1 ligne = 1 chunk) ;
  - copie toutes les métadonnées utiles (type de formation, établissement, commune, apprentissage, frais, sélectivité, etc.) sur chaque chunk ;
  - ajoute :

    - `chunk_index` : position du chunk dans le document (0, 1, 2, …) ;
    - `chunk_id` : identifiant unique du chunk.

Ce DataFrame “explosé” sert ensuite de base pour le calcul des embeddings et la construction de la base vectorielle.

### Embeddings et vector store (version actuelle)

La version actuellement déployée utilise les **embeddings OpenAI** :
- modèle d’embedding : `text-embedding-3-small` (OpenAI), dimension **1536** ;
- calcul des embeddings offline (notebook) via l’API OpenAI pour chaque `chunk_text` ;
- stockage dans une colonne `embedding` de type `vector(1536)` dans Postgres (extension `pgvector`).

Pipeline de préparation (notebook `13_full_vector_store.ipynb`) :
1) Charger les données Parcoursup nettoyées.
2) Appliquer `explode_chunks` pour obtenir un DataFrame de chunks.
3) Appeler `build_vector_store(df_chunks)` dans `vector_store.py` :
    - `embed_texts_batched(...)` appelle l’API OpenAI par batch pour calculer les embeddings.
    - Le DataFrame `df_vs` contient `chunk_id`, `chunk_text`, métadonnées, `embedding`.
4) Insérer / mettre à jour ces lignes dans la table `formations_chunks_vectors` via `upsert_chunks` (dans `pgvector_store.py`), en batch pour ne pas surcharger la base.

### Base vectorielle pgvector (prod)

En prod, la base vectorielle est hébergée sur Supabase :
- SGBD : PostgreSQL managé par Supabase.
- Extension : `CREATE EXTENSION IF NOT EXISTS vector;` pour activer le type vector et l’opérateur `<=>`.
- Table principale : `formations_chunks_vectors`
    - `chunk_id` (PRIMARY KEY)
    - métadonnées : `chunk_index`, `chunk_text`, `type_formation`, `type_etablissement`, `commune`, `is_apprentissage`, `frais_scolarite`, `formation_selective`, `formation_ouverte_boursiers`, …
    - `embedding vector(1536)` : vecteur OpenAI `text-embedding-3-small`.

Insertion côté Python : `src/backend/pgvector_store.py` expose `upsert_chunks(df_vs, batch_size=...)` qui fait un `INSERT ... ON CONFLICT (chunk_id) DO UPDATE` par batch.

La connexion à la base se fait via `get_pg_connection()` qui lit :
- en priorité `DATABASE_URL` (URI Postgres ou Session Pooler Supabase),
- sinon les variables `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`.

En prod (Render), on configure `DATABASE_URL` avec la chaîne de connexion Supabase.

## Moteur de recommandation RAG
### Profils lycéens structurés

- `profile_schema.py` définit `StudentProfile` (TypedDict) avec trois blocs :
  - contraintes objectives : `type_formation`, `is_apprentissage`, `max_frais_scolarite`, `commune` ;
  - intérêts et matières : `domains_interet`, `matieres_aimees`, `matieres_evitees` ;
  - style de travail / rythme : `preference_rythme`, `preference_travail`, `niveau_idee_orientation`.

- `profile_from_text.py` utilise `gpt-4o-mini` pour inférer un `StudentProfile` à partir d’un message libre :
  - le LLM renvoie un JSON strict avec uniquement les clés du profil, sans interprétation psychologique ni inférences sensibles.

### Recommandation avec filtres + similarité

- `recommendation.py` :
  - `build_filters_from_profile(profile)` traduit le profil en filtres SQL (`type_formation, is_apprentissage, max_frais_scolarite, commune` si possible).
  - `recommend_from_profile(profile, query_embedding, limit)` :
    - construit un `WHERE` SQL à partir des filtres,
      - exécute une requête RAG sur `formations_chunks_vectors` :
        - `ORDER BY embedding <=> (%s::vector)` (distance cosinus) pour classer les chunks,
      - regroupe les résultats par `chunk_id` et conserve, pour chaque formation, le chunk le plus pertinent.

Pour chaque formation retournée, la fonction ajoute :
- un objet reason avec des indicateurs comme match_type_formation, match_apprentissage, under_budget ;
- une phrase courte explanation en français, expliquant en quoi la formation correspond (type de diplôme, apprentissage, budget, etc.).

Ces champs sont utilisés ensuite pour la transparence dans le chat.

### Chaîne d’orientation RAG + LLM
Le fichier chat_pipeline.py orchestre toute la chaîne :

1) Profil structuré :
infer_profile_from_text(message) (dans profile_from_text.py) transforme le message libre en StudentProfile.
2) Embedding de la requête :
get_query_embedding(message) (dans embeddings.py) encode la question en vecteur 1536 via text-embedding-3-small.
3) Recommandations RAG :
recommend_from_profile(profile, query_emb, limit) interroge Supabase/pgvector pour récupérer les formations pertinentes avec reason et explanation.
4) Construction du contexte RAG :
le code construit un rag_context contenant, pour chaque reco :
    - type de formation, commune, frais,
    - un extrait tronqué du texte de la fiche,
    - explanation.
5) Appel au LLM conseiller :
call_llm_advisor(...) utilise gpt-4o-mini avec :
    - un system_prompt centré sur l’orientation, les contraintes de neutralité et la transparence ;
    - un message assistant contenant l’historique du chat (réformaté), le JSON du StudentProfile et la liste des formations (rag_context) ;
    - le message utilisateur actuel.

Le LLM doit :
- s’appuyer uniquement sur les formations remontées par le RAG (pas d’invention de ville ou de diplôme) ;
- expliquer en langage naturel pourquoi chaque suggestion colle au profil et aux contraintes (en s’appuyant sur explanation) ;
- citer au plus 3 formations, avec une explication courte par formation ;
- conclure en rappelant que ce sont des pistes à discuter avec un adulte/CO.

La longueur des réponses est plafonnée à environ 400 tokens pour contrôler les coûts et garder des réponses lisibles.

## API FastAPI
Le backend expose deux endpoints principaux :
- POST /recommendations
    - Reçoit { "question": str, "profile": StudentProfile, "limit": int }.
    - Encode la question en embedding, applique recommend_from_profile et renvoie :
`json:
{ "recommendations": [ ... ] }`

- POST /chat-orientation
  - Reçoit { "message": str, "history": [ { "role": "...", "content": "..." }, ... ] }.
  - Applique la chaîne complète (profil structuré + RAG + LLM conseiller).
  - Renvoie :
`json:
{ "answer": "<texte explicatif pour le lycéen>" }`

Des endpoints temporaires de debug (/health-db, /debug-db-url) peuvent être ajoutés ponctuellement pour vérifier la connexion à Supabase (non indispensables en prod).

## Intégration avec le front Next.js
Côté front, la route Next.js `/api/chat` joue le rôle d’adaptateur :
- lit la variable `ORIENTATION_API_URL` (par exemple http://127.0.0.1:8000 en local, ou l’URL Render en prod) ;
- envoie le dernier message utilisateur et l’historique vers `/chat-orientation` du backend ;
- renvoie au front un objet de la forme `{ "id": "<timestamp>", "role": "assistant", "content": "<answer>" }`.

L’interface de chat se contente d’afficher une liste de messages role / content en provenance de cette route.

## Déploiement (actuel)
- Backend FastAPI : déployé sur Render (plan gratuit 512 Mo), auto‑deploy depuis GitHub.
  - Commande de démarrage : `uvicorn src.backend.api:app --host 0.0.0.0 --port 8000`.
  - Variable d’environnement critique :
    - `DATABASE_URL` = URI Postgres/Session Pooler Supabase.
    - `OPENAI_API_KEY` pour les embeddings et le LLM.

- **Base de données** : projet Supabase (plan gratuit) hébergeant :
  - la table formations_chunks_vectors avec embedding vector(1536) ;
  - la connexion se fait via psycopg2 dans pgvector_store.py.

## Pistes d’évolution pour plus de souveraineté
Actuellement, le backend dépend :
- d’OpenAI pour les embeddings (text-embedding-3-small) et le LLM (gpt-4o-mini) ;
- de Supabase (Postgres managé) pour la base vectorielle.

Pour renforcer la souveraineté et réduire la dépendance à des services propriétaires, plusieurs évolutions sont possibles :

1) Revenir à des embeddings open‑source self‑hosted
  - Réactiver l’ancienne version basée sur multilingual-e5-base (Hugging Face, open‑source) via SentenceTransformer.
  - Héberger ce modèle sur un serveur (ou un conteneur Docker) dédié, éventuellement chez un fournisseur européen.
  - Recalculer les embeddings des chunks avec ce modèle et repasser la colonne embedding à la dimension E5 (768).

2) Self‑host de la base Postgres / pgvector
  - Remplacer Supabase par un Postgres+pgvector auto‑hébergé (Docker sur un VPS européen), en réutilisant pgvector_store.py tel quel.
  - Adapter DATABASE_URL pour pointer vers ce serveur plutôt que Supabase.
  - Se diriger vers Scalingo qui est hébergé sur Scaleway pour le déploiement du projet (frontend, backend et vector store).

3) LLM souverain / open‑source
  - Remplacer gpt-4o-mini par un LLM open‑source (par exemple Mistral ou Qwen) exposé via une API compatible (/v1/chat/completions) ou via un fournisseur européen.
  - Adapter profile_from_text.py et call_llm_advisor pour appeler ce nouveau modèle au lieu de l’API OpenAI.

4) Séparation claire des chemins “cloud” et “self‑host”
  - Garder dans le code deux implémentations parallèles :
    - un chemin “cloud” (OpenAI + Supabase, pratique pour le MVP et les démos) ;
    - un chemin “souverain” (embeddings E5 + Postgres auto‑hébergé + LLM open‑source), activable via une variable d’environnement ou un flag de configuration.

Ces pistes pourront être détaillées dans le mémoire comme des axes d’industrialisation future, tout en montrant que l’architecture actuelle reste compatible avec une migration vers plus de souveraineté.