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