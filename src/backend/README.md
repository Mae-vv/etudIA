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

## À faire

- Ajouter les endpoints de l’API.
- Décrire le pipeline complet de traitement.