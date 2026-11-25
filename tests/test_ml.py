"""Tests des fonctions de calcul (sans fichier EEG réel)."""

import numpy as np

from ml.cnn import prepare_cnn_input
from ml.evaluation import subject_accuracy
from ml.features import extract_features


def fake_epochs(n=3):
    rng = np.random.default_rng(0)
    return rng.normal(size=(n, 19, 6250)).astype(np.float32)


def test_extract_features_shape():
    assert extract_features(fake_epochs()).shape == (3, 247)


def test_prepare_cnn_input_shape_and_normalisation():
    x = prepare_cnn_input(fake_epochs() * 1e-5 + 3e-6)
    assert x.shape == (3, 6250, 19)
    assert np.allclose(x.mean(axis=1), 0, atol=1e-3)
    assert np.allclose(x.std(axis=1), 1, atol=1e-2)


def test_subject_accuracy_majority_vote():
    y = np.array([0, 0, 0, 1, 1, 1])
    groups = np.array(["h01", "h01", "h01", "s01", "s01", "s01"])
    y_pred = np.array([0, 0, 1, 0, 1, 1])
    assert subject_accuracy(y, y_pred, groups) == (2, 2)