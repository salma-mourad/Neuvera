

"""Prétraitement des signaux EEG, partagé par l'entraînement et l'application."""

import mne

# Paramètres du prétraitement : une seule source de vérité
L_FREQ = 1.0
H_FREQ = 45.0
EPOCH_DURATION = 25.0
SFREQ = 250.0

# Les 19 électrodes, dans un ordre fixe
CHANNELS = [
    "Fp2", "F8", "T4", "T6", "O2", "Fp1", "F7", "T3", "T5", "O1",
    "F4", "C4", "P4", "F3", "C3", "P3", "Fz", "Cz", "Pz",
]

def load_raw(path):
    return mne.io.read_raw_edf(path, preload=True, verbose=False)

def check_raw(raw):
    """Vérifie que le fichier ressemble aux données d'entraînement."""
    if raw.info["sfreq"] != SFREQ:
        raise ValueError(f"Fréquence attendue {SFREQ} Hz, reçu {raw.info['sfreq']} Hz")
    manquantes = set(CHANNELS) - set(raw.ch_names)
    if manquantes:
        raise ValueError(f"Électrodes manquantes : {sorted(manquantes)}")

def clean_raw(raw):
    """Référence moyenne + filtre passe-bande, sur une copie."""
    raw = raw.copy()
    raw.reorder_channels(CHANNELS)
    raw.set_eeg_reference(verbose=False)
    raw.filter(l_freq=L_FREQ, h_freq=H_FREQ, verbose=False)
    return raw

def make_epochs(raw):
    """Découpe en époques. Renvoie un tableau (n_epochs, 19, 6250)."""
    epochs = mne.make_fixed_length_epochs(
        raw, duration=EPOCH_DURATION, preload=True, verbose=False
    )
    return epochs.get_data()

def preprocess_file(path):
    """Pipeline complet : lecture, vérification, nettoyage, découpage."""
    raw = load_raw(path)
    check_raw(raw)
    raw = clean_raw(raw)
    return make_epochs(raw)