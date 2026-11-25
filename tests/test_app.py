"""Tests de l'application web (l'analyse EEG est simulée)."""

import io

import pytest

from app import create_app, services
from app.extensions import db

FAKE_RESULT = {"n_epochs": 37, "proba_logistic": 0.2, "proba_cnn": 0.3, "proba_final": 0.25, "label": 0}


@pytest.fixture
def client(tmp_path, monkeypatch):
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "UPLOAD_DIR": tmp_path,
    })
    monkeypatch.setattr(services, "analyze_file", lambda path: FAKE_RESULT)
    with app.app_context():
        db.create_all()
        yield app.test_client()


def register(client, email="medecin@test.fr"):
    return client.post("/auth/register", data={
        "name": "Dr Test", "email": email, "password": "motdepasse", "confirm": "motdepasse",
    }, follow_redirects=True)


def add_patient(client):
    return client.post("/patients/new", data={
        "first_name": "Ali", "last_name": "Test", "birth_date": "1990-05-01", "sex": "M",
    }, follow_redirects=True)


def test_pages_protegees_sans_connexion(client):
    assert client.get("/dashboard").status_code == 302


def test_inscription_puis_tableau_de_bord(client):
    response = register(client)
    page = response.get_data(as_text=True)
    assert "Dr Test" in page and "Dernière analyse" in page


def test_analyse_complete(client):
    register(client)
    add_patient(client)
    response = client.post("/patients/1/analyse", data={
        "eeg_file": (io.BytesIO(b"faux contenu"), "h01.edf"),
        "suspicion_level": "Faible",
        "family_history": "non",
    }, content_type="multipart/form-data", follow_redirects=True)
    page = response.get_data(as_text=True)
    assert "Profil sain" in page


def test_un_medecin_ne_voit_pas_les_patients_d_un_autre(client):
    register(client, "a@test.fr")
    add_patient(client)
    client.post("/auth/logout")
    register(client, "b@test.fr")
    assert client.get("/patients/1").status_code == 404