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
5. Ajout d'un indicateur binaire valant 1 si la formation est identifiée comme “Formations en apprentissage”, 0 sinon (voir `is_apprentissage`)
6. Ajout d'un code entier décrivant la présence d’un internat (0 = pas d’internat connu, 1 = internat pour filles et garçons, 2 = internat uniquement pour filles, 3 = internat uniquement pour garçons) (voir `internat_code`)

Ces variables sont calculées dans src/backend/processing.py

Ce pipeline est utilisé dans le notebook `traitement.ipynb` pour générer la version nettoyée des données, utilisée ensuite par l’IA d’orientation.

> Règle : cette section doit être mise à jour dès qu’un nouveau filtre important est ajouté
> ou que des colonnes sont supprimées / renommées de façon durable.

## 4. Bonnes pratiques d’usage dans ce projet

- Vérifier la date de téléchargement et la cohérence avec la campagne Parcoursup analysée.
- Mettre à jour la liste des filtres et transformations dès qu’un changement structurel est fait dans le code.
- Mentionner la source et la licence dans les livrables et visualisations.
