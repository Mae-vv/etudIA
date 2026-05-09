# Données du projet etudIA

Ce dossier contient les données utilisées pour analyser l’offre de formations Parcoursup (géolocalisation, type de formation, statut, capacité d’accueil, etc.).

## 1. Jeu de données utilisé

- Nom du jeu de données : « Cartographie des formations Parcoursup » (`fr-esr-cartographie_formations_parcoursup`)
- Producteur : Ministère de l’Enseignement supérieur et de la Recherche
- Licence : Licence Ouverte / Open Licence 2.0
- Portail open data : data.enseignementsup-recherche.gouv.fr / data.gouv.fr

## 2. Source et téléchargement

- Source : fichier téléchargé depuis le portail open data du MESR (jeu de données « Cartographie des formations Parcoursup »)
- URL de référence :  
  https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-cartographie_formations_parcoursup/information/
- Date de téléchargement : 2026-01-18
- Format : export CSV

## 3. Préparation des données (version actuelle)

Cette section décrit l’état actuel du fichier préparé utilisé dans le projet.

Étapes actuelles du pipeline :
1. Chargement du CSV brut avec `load_parcoursup_csv(path)`
2. Suppression des colonnes non nécessaires avec `drop_unused_columns(df)` (voir liste UNUSED_COLUMNS dans `processing.py`)
3. Renommage des colonnes pour des noms plus explicites avec `rename_columns(df)` (mapping RENAMING_MAP)
4. Filtre sur la campagne cible (par exemple `session == "2026"`) avec `filter_target_year(df, year)`


#### Variables dérivées 

1. is_apprentissage : 1 si la formation est proposée en apprentissage, 0 sinon
2. internat_code : codage de la disponibilité d’un internat (0 = pas d’internat, 1 = internat filles et garçons, 2 = internat réservé aux filles, 3 = internat réservé aux garçons)
3. is_presentiel : 1 si la formation peut être suivie en présentiel, 0 sinon
4. is_partiel_distance : 1 si la formation est partiellement à distance, 0 sinon
5. is_full_distance : 1 si la formation est entièrement à distance, 0 sinon
6. has_sport_amenagement : 1 si des aménagements sont prévus pour les sportifs de haut niveau, 0 sinon.
7. has_artist_amenagement : 1 si des aménagements sont prévus pour des artistes confirmés, 0 sinon
8. has_other_amenagement : 1 si des aménagements sont prévus pour d’autres publics spécifiques, 0 sinon

Ces variables sont calculées dans src/backend/processing.py

Ce pipeline est utilisé dans le notebook `traitement.ipynb` pour générer la version nettoyée des données, utilisée ensuite par l’IA d’orientation.

> Règle : cette section doit être mise à jour dès qu’un nouveau filtre important est ajouté
> ou que des colonnes sont supprimées / renommées de façon durable.

## 4. Bonnes pratiques d’usage dans ce projet

- Vérifier la date de téléchargement et la cohérence avec la campagne Parcoursup analysée.
- Mettre à jour la liste des filtres et transformations dès qu’un changement structurel est fait dans le code.
- Mentionner la source et la licence dans les livrables et visualisations.

## 5. Fichier enrichi Parcoursup 2026

- Nom du fichier : `parcoursup_2026_enriched.csv`
- Origine :
  - Base : jeu de données Parcoursup 2026 (cartographie des formations).
  - Enrichissement : scraping des fiches formations publiques Parcoursup (colonne `link_formation`).
- Colonnes ajoutées (principales) :
  - `presentation` : texte de présentation de la formation.
  - `criteres_entree` : attendus nationaux et complémentaires, éléments de grille d’analyse.
  - `debouches_professionnels`, `poursuite_etudes` : poursuites d’études et débouchés.
  - `frais_scolarite`, `frais_scolarite_boursiers` : coûts estimés de la formation.
  - `langues_options` : langues vivantes et options proposées.
  - `nb_places` : nombre de places annoncées.
  - `formation_ouverte_boursiers`, `diplome_controle_par_etat`, `formation_selective`,
    `epreuves_selection`, `frais_candidature`, `frais_candidature_boursiers`.
- Limites :
  - Les informations de scraping ne sont pas disponibles pour toutes les formations
    (structure de fiche différente ou sections absentes), ce qui entraîne un taux élevé
    de valeurs manquantes pour certaines colonnes.
  - Les montants restent pour l’instant des chaînes de caractères (formats monétaires
    hétérogènes) et pourront être transformés plus tard selon les besoins d’analyse.
  
## 6. Ajout d'une colonne pour le RAG

- Nom du fichier : `parcoursup_2026_enriched_rag.csv`
- Colonne ajoutée : 
  - `rag_document` : ligne qui concatène nom de la formation, établissement, présentation
    critères d’entrée, poursuites d’études, débouchés et infos de sélection pour servir
    de support au futur RAG.

# Préparation RAG pour l’aide à l’orientation

L’objectif est de préparer les données Parcoursup pour un futur système de RAG 
(Retrieval Augmented Generation) utilisé par l’IA d’aide à l’orientation des lycéens.
​
## 1. Source de vérité

- Base de départ : parcoursup_2026_enriched.csv (données Parcoursup nettoyées + informations scrappées).
- Chaque ligne représente une formation unique.
​
## 2. Document RAG (rag_document)

Pour chaque formation, une colonne rag_document est construite à partir d’un texte concaténé comprenant
notamment :
- Nom de la formation (name_formation)
- Type de formation (type_formation)
- Nom et type d’établissement, avec localisation (name_etablissement, type_etablissement, commune, departement, region)
- Mentions / spécialités (mentions_specialites)
- Présentation de la formation (presentation)
- Critères d’entrée et attendus (criteres_entree)
- Poursuites d’études (poursuite_etudes)
- Débouchés professionnels (debouches_professionnels)
- Informations sur la sélectivité (formation_selective)
- Éventuelles épreuves de sélection (epreuves_selection)

Ce texte est ensuite destiné à être vectorisé pour la recherche sémantique.
​
## 3. Filtres et métadonnées structurées

En parallèle, plusieurs colonnes restent des filtres structurés (non concaténés dans rag_document) pour
guider la recherche et expliciter les recommandations :
- Localisation : region, departement, commune
- Modalités : is_apprentissage, is_presentiel, is_partiel_distance, is_full_distance
- Accès et capacité : nb_places, formation_selective (0/1), epreuves_selection
- Coûts : frais_scolarite, frais_scolarite_boursiers, frais_candidature, frais_candidature_boursiers
- Conditions particulières : formation_ouverte_boursiers, internat_code, has_sport_amenagement, has_artist_amenagement, has_other_amenagement

Ces colonnes permettront, au moment de la requête, de filtrer les formations (par exemple “BUT en apprentissage
en Bretagne, peu onéreux, avec internat”) et d’expliquer clairement les critères utilisés.
​
## 4. Chunking et embeddings

Avant la vectorisation, les contenus rag_document pourront être découpés en chunks de taille raisonnable
(blocs de longueur limitée) pour :
- respecter les limites de longueur des modèles d’embeddings,
- améliorer la précision de la recherche,
- éviter de mélanger trop d’informations hétérogènes dans un même vecteur.

### Analyse de la longueur des documents RAG et choix du chunking

Un notebook d’exploration (`05_rag_documents_lengths.ipynb`) analyse la longueur de la colonne `rag_document` (en caractères) à partir du fichier `parcoursup_2026_enriched_rag.csv`.

Principaux résultats (ordre de grandeur) :
- médiane de la longueur de `rag_document` : ~361 caractères ;
- une moyenne situé autour de 848.5 caractères ;
- maximum observé : ~6857 caractères ;
- plus de 3 000 formations ont un `rag_document` de plus de 1 000 caractères.

Ces valeurs montrent que certaines lignes utile au RAG sont relativement longues (présentation + critères d’entrée + poursuites d’études + débouchés + sélection). Pour éviter des vecteurs trop longs et améliorer la précision de la recherche sémantique, la base vectorielle sera construite à partir de **chunks** de texte :

- chaque `rag_document` sera découpé en segments de taille raisonnable (ordre de grandeur : **1 500 à 2 000 caractères** par chunk, soit environ 500–800 tokens) ;
- chaque chunk héritera des mêmes métadonnées que la formation d’origine (type de formation, région, apprentissage, coûts, internat, aménagements, etc.) ;
- la recherche RAG se fera sur les embeddings de ces chunks, après filtrage préalable sur les colonnes structurées.

Ce choix de chunking permet :
- de rester compatible avec les limites des modèles d’embeddings,
- de limiter le mélange d’informations hétérogènes dans un même vecteur,
- de garder des réponses plus ciblées pour les lycéens.

### DataFrame de chunks pour la base vectorielle

À partir du fichier `parcoursup_2026_enriched_rag.csv`, un DataFrame de chunks est généré afin de préparer la création de la base vectorielle. Chaque ligne du fichier `parcoursup_2026_enriched_chunks.csv` correspond à un **chunk** d’un `rag_document` (et non plus à une formation entière).

- Le texte complet `rag_document` est découpé en segments de taille raisonnable (≈ 1 500–2 000 caractères, soit environ 500–800 tokens).
- Chaque chunk est stocké dans la colonne `chunk_text` et identifié par :
  - `chunk_id` : identifiant unique du chunk ;
  - `chunk_index` : position du chunk dans le document original (0, 1, 2, …).
- Toutes les métadonnées de la formation d’origine (type de formation, région, apprentissage, coûts, internat, aménagements, etc.) sont recopiées sur chaque chunk.

Ce fichier de chunks sert de point de départ pour calculer les embeddings et construire la future base vectorielle utilisée par le système de RAG.

## 5. Flux RAG envisagé

- Étape 1 : le lycéen pose une question en langage naturel.
- Étape 2 : le système analyse la question et en extrait des contraintes de filtrage
(ex. type de formation, région, apprentissage, coûts).
- Étape 3 : application des filtres sur les colonnes structurées du dataset.
- Étape 4 : recherche sémantique sur les rag_document (ou leurs chunks) des formations filtrées,
à l’aide d’embeddings.
- Étape 5 : génération d’une réponse expliquant les formations proposées, en mentionnant explicitement
les critères utilisés (coût, localisation, sélectivité, poursuites d’études, etc.).

## 6. Lien avec la base pgvector (DB)

Les fichiers préparés servent de source à la base vectorielle utilisée en production :

- `parcoursup_2026_enriched_chunks.csv` est chargé par le script backend (`src/backend/vector_store.py` / `pgvector_store.py`) pour :
  - calculer les embeddings (`chunk_text` → vecteurs),
  - insérer chaque chunk et ses métadonnées dans la table Postgres/pgvector.
- La base pgvector est ensuite interrogée par l’API FastAPI `/chat-orientation` pour récupérer les formations pertinentes à chaque question (filtres structurés + similarité de `chunk_text`).

Ainsi, **ce dossier `src/data` est la “source de vérité”** pour les données Parcoursup, et la DB n’en est qu’un dérivé optimisé pour la recherche.