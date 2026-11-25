"""Configuration de l'application, lue depuis le fichier .env."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cle-de-developpement-a-changer")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'instance' / 'neuvera.db'}"
    UPLOAD_DIR = BASE_DIR / "instance" / "uploads"
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024