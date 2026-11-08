"""Prétraite tous les fichiers EDF de data/raw/ et sauvegarde les époques dans data/processed/."""

from pathlib import Path

import numpy as np

from ml.preprocessing import preprocess_file

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fichiers = sorted(RAW_DIR.glob("*.edf"))

    for path in fichiers:
        epochs = preprocess_file(path).astype(np.float32)
        np.save(OUT_DIR / f"{path.stem}.npy", epochs)
        print(f"{path.name} : {epochs.shape[0]} époques")

    print(f"Terminé : {len(fichiers)} fichiers traités.")


if __name__ == "__main__":
    main()