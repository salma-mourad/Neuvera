# Neuvera

Plateforme web d'analyse EEG assistée par l'IA : dépôt d'un enregistrement EEG, prétraitement, classification par deux modèles (régression logistique et CNN 1D) et rapport par patient.

**Stack :** Python · MNE · scikit-learn · TensorFlow/Keras · Flask · SQLAlchemy · PostgreSQL

> Outil de recherche, pas un dispositif médical.

## Contexte

Neuvera est notre projet de fin d'études de licence, réalisé en équipe de trois à la Faculté des Sciences Ben M'Sik (Université Hassan II).

Ce dépôt contient ma propre version du projet, reconstruite à partir du code de l'équipe avec une architecture revue et plusieurs corrections :

- prétraitement écrit une seule fois et partagé par l'entraînement et l'application ;
- vérification des fichiers en entrée (fréquence, électrodes, ordre des canaux) ;
- analyse de **toutes** les époques du signal, et non de la première seule ;
- évaluation **par sujet**, pour éviter la fuite de données entre entraînement et test.

## Données

[EEG in schizophrenia](https://repod.icm.edu.pl/dataset.xhtml?persistentId=doi:10.18150/repod.0107441) (RepOD, licence CC0) : 28 sujets (14 sains, 14 atteints de schizophrénie paranoïde), 19 électrodes (système 10-20), 250 Hz, environ 15 minutes de repos les yeux fermés par sujet.

Les fichiers ne sont pas versionnés : les télécharger dans `data/raw/`.

## Pipeline

```text
EDF brut (19 × ~230 000 mesures)
  → vérification (250 Hz, 19 électrodes, ordre fixe)
  → référence moyenne + filtre passe-bande 1–45 Hz
  → découpage en époques de 25 s (19 × 6 250)
  ├─ 13 statistiques × 19 électrodes = 247 features → régression logistique
  └─ signal normalisé (6 250 × 19)                   → CNN 1D
  → moyenne des probabilités sur toutes les époques → rapport
```

## Résultats

Validation croisée en 7 plis, **groupée par sujet** (un sujet n'est jamais à la fois en entraînement et en test).

| Modèle | Précision par époque | Sujets bien classés |
|---|---|---|
| Référence (classe majoritaire) | 54,8 % | 14/28 |
| Régression logistique | 68,0 % | 19/28 |
| CNN 1D | 76,3 % | 22/28 |

Pour comparaison, mélanger les époques sans tenir compte des sujets donne 87,8 % pour la régression logistique : l'écart de 20 points vient de la fuite de données (le modèle reconnaît les sujets, pas la maladie).

**Limites :** 28 sujets seulement, un seul jeu de données, un seul protocole d'enregistrement. L'écart entre les deux modèles (3 sujets) reste faible à cette échelle, et les résultats ne se généralisent pas à d'autres populations sans validation externe.

## Architecture

```text
app/         application Flask (routes, modèles SQLAlchemy, gabarits, services)
ml/          prétraitement, features, CNN, évaluation, prédiction
scripts/     traitement par lot et entraînement des modèles
notebooks/   exploration des données
artifacts/   modèles entraînés
tests/       tests automatiques
```

## Lancer le projet

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements-dev.txt

# Données et modèles
python -m scripts.preprocess_all
python -m scripts.train_ml
python -m scripts.train_cnn

# Application
cp .env.example .env        # puis remplir SECRET_KEY et, si besoin, DATABASE_URL
python -m flask --app app init-db
python -m flask --app app run --port 5001

# Tests
python -m pytest
```