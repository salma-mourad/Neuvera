"""Outils d'évaluation partagés par les scripts d'entraînement."""

import numpy as np


def subject_accuracy(y, y_pred, groups):
    """Vote majoritaire : un sujet est bien classé si la majorité de ses époques l'est."""
    sujets = np.unique(groups)
    corrects = 0
    for s in sujets:
        masque = groups == s
        vote = int(np.mean(y_pred[masque]) >= 0.5)
        corrects += int(vote == y[masque][0])
    return corrects, len(sujets)