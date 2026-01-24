# Données du projet

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

- **Filtre d’année** : seules les lignes correspondant à l’année 2026 sont conservées  
  (objectif : se concentrer sur l’offre de formation actuelle).
- **Colonnes supprimées** (peu utiles pour l’analyse actuelle et pour simplifier le jeu) :  
  `Localisation`, `etablissement_id_paysage`, `composante_id_paysage`, `rnd`,  
  `Lien vers les données statistiques pour l'année antérieure`,  
  `code interne parcoursup de la formation`,  
  `code interne parcoursup pour les portails`, `code_formation`.
- **Colonnes renommées** (exemples) :  
  - `nom long de la formation` → `name_formation` (nom plus court, utilisable dans le code)  
  - `identifiant de l'établissement` → `id_etablissement` (raccourcissement des noms, suppression des espaces/accents)

> Règle : cette section doit être mise à jour dès qu’un nouveau filtre important est ajouté
> ou que des colonnes sont supprimées / renommées de façon durable.

## 4. Bonnes pratiques d’usage dans ce projet

- Vérifier la date de téléchargement et la cohérence avec la campagne Parcoursup analysée.
- Mettre à jour la liste des filtres et transformations dès qu’un changement structurel est fait dans le code.
- Mentionner la source et la licence dans les livrables et visualisations.
