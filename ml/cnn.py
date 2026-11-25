"""Réseau de neurones convolutif 1D pour les époques EEG."""

import numpy as np


def prepare_cnn_input(epochs):
    """Transforme (n_epochs, 19, n_times) en (n_epochs, n_times, 19), normalisé."""
    x = epochs.astype(np.float32)
    x = (x - x.mean(axis=-1, keepdims=True)) / (x.std(axis=-1, keepdims=True) + 1e-8)
    return np.transpose(x, (0, 2, 1))


def build_cnn(n_times=6250, n_channels=19):
    """Petit CNN 1D : trois convolutions, puis une sortie sigmoïde."""
    from tensorflow import keras
    from tensorflow.keras import layers

    model = keras.Sequential([
        layers.Input(shape=(n_times, n_channels)),
        layers.Conv1D(16, 7, strides=2, activation="relu"),
        layers.MaxPooling1D(4),
        layers.Conv1D(32, 7, activation="relu"),
        layers.MaxPooling1D(4),
        layers.Conv1D(64, 7, activation="relu"),
        layers.GlobalAveragePooling1D(),
        layers.Dropout(0.5),
        layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model