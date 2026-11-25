"""Entraîne et évalue le CNN 1D (validation par sujet), puis sauvegarde le modèle."""

from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedGroupKFold

from ml.cnn import build_cnn, prepare_cnn_input
from ml.evaluation import subject_accuracy

PROCESSED_DIR = Path("data/processed")
MODEL_PATH = Path("artifacts/cnn_model.keras")
N_EPOCHS = 15
BATCH_SIZE = 32


def load_dataset():
    """Renvoie X (n, 6250, 19), y et groups."""
    X, y, groups = [], [], []
    for path in sorted(PROCESSED_DIR.glob("*.npy")):
        x = prepare_cnn_input(np.load(path))
        label = 1 if path.stem.startswith("s") else 0
        X.append(x)
        y.append(np.full(len(x), label))
        groups.append(np.full(len(x), path.stem))
    return np.concatenate(X), np.concatenate(y), np.concatenate(groups)


def main():
    from tensorflow import keras

    keras.utils.set_random_seed(0)
    X, y, groups = load_dataset()
    print("X :", X.shape)

    cv = StratifiedGroupKFold(n_splits=7, shuffle=True, random_state=0)
    pred = np.zeros(len(y), dtype=int)
    for k, (train_idx, test_idx) in enumerate(cv.split(X, y, groups)):
        model = build_cnn()
        model.fit(X[train_idx], y[train_idx], epochs=N_EPOCHS, batch_size=BATCH_SIZE, verbose=0)
        pred[test_idx] = (model.predict(X[test_idx], verbose=0).ravel() >= 0.5).astype(int)
        print(f"Pli {k + 1}/7 terminé")

    print(f"Validation par sujet, par époque : {accuracy_score(y, pred):.1%}")
    corrects, total = subject_accuracy(y, pred, groups)
    print(f"Validation par sujet, par sujet : {corrects}/{total}")

    final_model = build_cnn()
    final_model.fit(X, y, epochs=N_EPOCHS, batch_size=BATCH_SIZE, verbose=0)
    MODEL_PATH.parent.mkdir(exist_ok=True)
    final_model.save(MODEL_PATH)
    print(f"Modèle sauvegardé : {MODEL_PATH}")


if __name__ == "__main__":
    main()