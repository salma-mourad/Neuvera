"""Entraîne et évalue la régression logistique, puis sauvegarde le modèle."""

from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from ml.evaluation import subject_accuracy
from ml.features import extract_features

PROCESSED_DIR = Path("data/processed")
MODEL_PATH = Path("artifacts/logistic_model.joblib")


def load_dataset():
    """Renvoie X (features), y (0 = sain, 1 = schizophrène) et groups (sujet)."""
    X, y, groups = [], [], []
    for path in sorted(PROCESSED_DIR.glob("*.npy")):
        feats = extract_features(np.load(path))
        label = 1 if path.stem.startswith("s") else 0
        X.append(feats)
        y.append(np.full(len(feats), label))
        groups.append(np.full(len(feats), path.stem))
    return np.concatenate(X), np.concatenate(y), np.concatenate(groups)


def build_model():
    """Standardisation puis régression logistique."""
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))


def main():
    X, y, groups = load_dataset()
    print("X :", X.shape)
    print("y :", y.shape, "| sains :", (y == 0).sum(), "| schizophrènes :", (y == 1).sum())
    print("Sujets :", len(np.unique(groups)))

    model = build_model()
    model.fit(X, y)
    print(f"Précision sur les données d'entraînement : {model.score(X, y):.1%}")

    cv_epoques = StratifiedKFold(n_splits=7, shuffle=True, random_state=0)
    pred_epoques = cross_val_predict(build_model(), X, y, cv=cv_epoques)
    print(f"Validation croisée (époques mélangées) : {accuracy_score(y, pred_epoques):.1%}")

    cv_sujets = StratifiedGroupKFold(n_splits=7, shuffle=True, random_state=0)
    pred_sujets = cross_val_predict(build_model(), X, y, groups=groups, cv=cv_sujets)
    print(f"Validation par sujet, par époque : {accuracy_score(y, pred_sujets):.1%}")
    corrects, total = subject_accuracy(y, pred_sujets, groups)
    print(f"Validation par sujet, par sujet : {corrects}/{total}")

    final_model = build_model()
    final_model.fit(X, y)
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(final_model, MODEL_PATH)
    print(f"Modèle sauvegardé : {MODEL_PATH}")


if __name__ == "__main__":
    main()