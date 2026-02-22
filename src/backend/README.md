# Backend etudIA

Ce dossier contient le code backend du projet etudIa (préparation des données Parcoursup, API d’orientation, etc.).

## Modules

- `processing.py` : fonctions de chargement et de nettoyage du jeu de données « Cartographie des formations Parcoursup ».

Les fonctions de traitement des données sont testées avec pytest.
Exemple : filter_target_year est vérifiée sur un DataFrame de test pour s’assurer qu’elle ne conserve que la session cible.

## À faire

- Ajouter les endpoints de l’API.
- Décrire le pipeline complet de traitement.