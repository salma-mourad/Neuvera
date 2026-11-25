"""Extraction des 13 caractéristiques statistiques par électrode."""

import numpy as np
from scipy import stats


def extract_features(epochs):
    """Transforme (n_epochs, 19, n_times) en (n_epochs, 247)."""
    feats = [
        epochs.mean(axis=-1),
        epochs.std(axis=-1),
        np.ptp(epochs, axis=-1),
        epochs.var(axis=-1),
        epochs.min(axis=-1),
        epochs.max(axis=-1),
        epochs.argmin(axis=-1),
        epochs.argmax(axis=-1),
        (epochs ** 2).mean(axis=-1),
        np.sqrt((epochs ** 2).mean(axis=-1)),
        np.abs(np.diff(epochs, axis=-1)).sum(axis=-1),
        stats.skew(epochs, axis=-1),
        stats.kurtosis(epochs, axis=-1),
    ]
    return np.concatenate(feats, axis=1)