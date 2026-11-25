"""Chargement des modèles entraînés et prédiction sur un enregistrement."""

from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

from ml.cnn import prepare_cnn_input
from ml.features import extract_features

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "artifacts"
LOGISTIC_PATH = ARTIFACTS_DIR / "logistic_model.joblib"
CNN_PATH = ARTIFACTS_DIR / "cnn_model.keras"
THRESHOLD = 0.5


@lru_cache(maxsize=1)
def _logistic_model():
    return joblib.load(LOGISTIC_PATH)


@lru_cache(maxsize=1)
def _cnn_model():
    from tensorflow import keras
    return keras.models.load_model(CNN_PATH)


def predict_epochs(epochs):

    proba_lr = _logistic_model().predict_proba(extract_features(epochs))[:, 1]
    result = {"n_epochs": int(len(epochs)), "proba_logistic": float(np.mean(proba_lr)), "proba_cnn": None}

    if CNN_PATH.exists():
        proba_cnn = _cnn_model().predict(prepare_cnn_input(epochs), verbose=0).ravel()
        result["proba_cnn"] = float(np.mean(proba_cnn))

    probas = [p for p in (result["proba_logistic"], result["proba_cnn"]) if p is not None]
    result["proba_final"] = float(np.mean(probas))
    result["label"] = int(result["proba_final"] >= THRESHOLD)
    return result