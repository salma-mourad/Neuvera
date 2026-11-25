"""Logique métier : enregistrement des fichiers et analyse, sans dépendance aux routes."""

import uuid
from pathlib import Path

from ml.predictors import predict_epochs
from ml.preprocessing import preprocess_file

ALLOWED_EXTENSIONS = {".edf"}


def is_allowed(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def save_upload(file_storage, upload_dir):
    """Enregistre le fichier sous un nom unique et renvoie ce nom."""
    upload_dir = Path(upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}.edf"
    file_storage.save(upload_dir / stored_name)
    return stored_name


def analyze_file(path):
    """Prétraitement complet puis prédiction des deux modèles."""
    try:
        epochs = preprocess_file(path)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError("fichier EDF illisible.") from e
    if len(epochs) == 0:
        raise ValueError("Enregistrement trop court : il faut au moins 25 secondes de signal.")
    return predict_epochs(epochs)