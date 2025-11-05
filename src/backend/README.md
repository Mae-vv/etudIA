# Base de données « Formations Parcoursup »

## 1. Description

Ce jeu de données recense l’ensemble des formations supérieures accessibles via la plateforme Parcoursup (public/privé sous contrat) pour les sessions 2020 à 2025, et à terme actualisé chaque année. Il permet, par exemple, d’explorer l’offre de formation (via carte interactive) et d’analyser les caractéristiques des formations (type, statut, géolocalisation, capacité d’accueil, etc.). ([Parcoursup][1])

## 2. Stockage de la donnée

* Le jeu de données est diffusé en open-data via les portails officiels du Ministère de l’Enseignement supérieur et de la Recherche ou via le portail national des données ouvertes. ([data.gouv.fr][2])
* Format de diffusion : fichiers CSV, JSON ; fichier ZIP pour certaines versions géographiques. ([data.gouv.fr][2])
* Identifiant du jeu de données : `fr-esr-cartographie_formations_parcoursup`. ([Data Éducation][3])
* Licence : Licence Ouverte / Open Licence 2.0. ([data.gouv.fr][2])
* Hébergement : sur data.gouv.fr ou data.education.gouv.fr (voir métadonnées du jeu de données). ([Data Éducation][4])

## 3. Propriétaire / Responsable

* Diffuseur / Gestionnaire : Ministère chargé de l’Enseignement supérieur et de la Recherche. ([data.gouv.fr][2])
* Éditeur : même ministère. ([data.gouv.fr][2])
* Origine : données issues de la plateforme Parcoursup et transformées pour la diffusion open-data. ([mesr.opendatasoft.com][5])

## 4. Mise à jour

* Pour le jeu « Cartographie des formations » : **mise à jour quotidienne**. ([data.gouv.fr][2])
* Concernant les campagnes de vœux / affectation (autre jeu de données) : les données sont publiées après la clôture de la session (ex. session 2024 du 17 janvier au 12 septembre) pour les formations hors apprentissage. ([data.gouv.fr][6])
* Note : pour la campagne 2025, certaines données sont « complétées au fur et à mesure jusqu’au 15 janvier ». ([data.enseignementsup-recherche.gouv.fr][7])

## 5. Taille de la base / volumétrie

* Le jeu de données « Cartographie des formations » couvre les formations proposées en 2020-2025. ([Data Éducation][4])
* L’interface indique que l’export en format géographique est limité à **50 000 enregistrements**. ([data.enseignementsup-recherche.gouv.fr][8])
* Selon la plateforme officielle, pour la session 2024 : le jeu « vœux de poursuite d’études et de réorientation » couvre « 14 079 formations hors apprentissage ». ([mesr.opendatasoft.com][5])
* **Remarque** : je n’ai pas trouvé de documentation publique précisant le nombre exact total d’enregistrements (lignes) pour le fichier CSV à jour, ni le poids en Mo/Go. Il conviendra de le mesurer directement après téléchargement.

## 6. Utilisation / réutilisation

* Licence ouverte – possibilité de réutilisation libre, sous réserve de mentionner la source conformément aux mentions légales. ([Parcoursup][9])
* À titre d’exemple, l’offre est d’environ « plus de 24 000 formations supérieures » pour la rentrée 2025. ([Parcoursup][1])

## 7. Exemple de lien / accès

* Lien vers le jeu de données : [Cartographie des formations Parcoursup](https://www.data.gouv.fr/datasets/cartographie-des-formations-parcoursup/) (via data.gouv.fr) ([data.gouv.fr][2])
* Export API possible : CSV, JSON selon le jeu. ([data.enseignementsup-recherche.gouv.fr][8])

## 8. Bonnes pratiques d’usage pour votre projet

* Vérifier la date de mise à jour et s’assurer que vous travaillez avec la version la plus récente (mise à jour quotidienne).
* Vérifier la lisibilité et cohérence des champs (identifiants des formations, types de formation, géolocalisation, capacité d’accueil…).
* Étant donnée la taille potentielle (des dizaines de milliers de lignes), prévoir un stockage et traitement appropriés (par ex. chargement dans PostgreSQL, indexation).
* Bien documenter toute transformation ou enrichissement que vous faites (nettoyage, agrégation, filtres) afin de garder la traçabilité de la donnée d’origine.
* Respecter les mentions de source/licence dans vos livrables ou site web.

---

[1]: https://www.parcoursup.gouv.fr/trouver-une-formation/quelles-formations-sont-accessibles-sur-parcoursup-1318?utm_source=chatgpt.com "Quelles formations sont accessibles sur Parcoursup"
[2]: https://www.data.gouv.fr/datasets/cartographie-des-formations-parcoursup/?utm_source=chatgpt.com "Cartographie des formations Parcoursup - Data.gouv"
[3]: https://data.education.gouv.fr/explore/dataset/fr-esr-cartographie_formations_parcoursup/export/?utm_source=chatgpt.com "Cartographie des formations Parcoursup - Éducation Nationale"
[4]: https://data.education.gouv.fr/explore/dataset/fr-esr-cartographie_formations_parcoursup/?utm_source=chatgpt.com "Cartographie des formations Parcoursup"
[5]: https://mesr.opendatasoft.com/explore/dataset/fr-esr-parcoursup/data/?utm_source=chatgpt.com "Parcoursup 2024 - vœux de poursuite d'études et de réorientation ..."
[6]: https://www.data.gouv.fr/fr/datasets/parcoursup-2022-voeux-de-poursuite-detudes-et-de-reorientation-dans-lenseignement-superieur-et-reponses-des-etablissements/?utm_source=chatgpt.com "Parcoursup 2024 - vœux de poursuite d'études et de réorientation ..."
[7]: https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-cartographie_formations_parcoursup/export/?utm_source=chatgpt.com "Cartographie des formations Parcoursup - Open data"
[8]: https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-cartographie_formations_parcoursup/export/?flg=fr-fr&utm_source=chatgpt.com "Cartographie des formations Parcoursup ..."
[9]: https://www.parcoursup.gouv.fr/mentions-legales-1320-1320?utm_source=chatgpt.com "Mentions légales | Parcoursup"
