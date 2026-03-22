# EtudIA – IA d’aide à l’orientation avant Parcoursup

EtudIA est un projet d’IA d’aide à l’orientation pour les lycéens avant Parcoursup.  
L’objectif est de proposer des recommandations de formations transparentes, équitables et conformes au RGPD, en s’appuyant sur les données ouvertes Parcoursup et des informations enrichies (présentation, critères d’entrée, débouchés, etc.).

## Architecture générale

- **Frontend** : application (ex. SDK Vercel) pour l’interface lycéen.
- **Backend Python** (dossier `src/backend/`) :
  - `processing.py` : chargement et nettoyage des données open source Parcoursup (suppression / renommage de colonnes, filtre sur l’année cible, etc.).
  - `scraping.py` : scraping et parsing des fiches formations (présentation, critères d’entrée, débouchés, frais, langues, nombre de places…).
- **Données** (dossier `data/`) :
  - `raw/` : fichiers bruts (export Cartographie des formations Parcoursup, etc.).
  - `processed/` : fichiers nettoyés et enrichis (dont `parcoursup_2026_enriched.csv` et la version avec `rag_document`).
  - Le fichier `data/README.md` documente la source des données, les transformations et la préparation RAG.

## Préparation RAG (haute vue)

- Chaque formation est représentée par :
  - un document texte `rag_document` (nom de la formation, établissement, présentation, critères d’entrée, poursuites d’études, débouchés, sélectivité, épreuves de sélection) pensé pour être lu par un lycéen ;
  - des filtres structurés (région, type de formation, apprentissage, distance, coûts, internat, aménagements, etc.) pour guider la recherche et expliciter les recommandations.
- Ce jeu de données servira ensuite de base à une future “base vectorielle” et à un pipeline de RAG (embeddings + recherche sémantique + génération de réponses).

## Base vectorielle et RAG

Le projet utilise une base PostgreSQL (Docker) avec l’extension `pgvector` pour stocker les embeddings des chunks de texte Parcoursup.  
Les embeddings sont générés en Python (Sentence Transformers, modèle multilingue e5-base) puis insérés dans la table `formations_chunks_vectors` via la fonction `upsert_chunks`.  
Les requêtes RAG combinent une similarité cosinus (`embedding <=> query_vector`) et, à terme, des filtres structurés (type de formation, apprentissage, région, coûts…) pour proposer des formations pertinentes aux lycéens.

## Objectifs du projet

- Aider les lycéens à comprendre et comparer les formations Parcoursup.
- Mettre en avant des critères d’équité (boursiers, aménagements, accessibilité, etc.).
- Assurer transparence sur les données utilisées et les décisions de l’IA (documentation des sources, des filtres et des transformations).
