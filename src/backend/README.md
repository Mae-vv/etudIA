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

## À faire

- Ajouter les endpoints de l’API.