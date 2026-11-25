"""Fabrique de l'application Flask."""

from pathlib import Path

from flask import Flask

from app.config import Config
from app.extensions import csrf, db, login_manager


def create_app(overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)
    Path(app.config["UPLOAD_DIR"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app import models

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(models.User, int(user_id))

    from app.routes.analysis import bp as analysis_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.patients import bp as patients_bp
    from app.routes.public import bp as public_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(public_bp)

    @app.cli.command("init-db")
    def init_db():
        """Crée les tables de la base de données."""
        db.create_all()
        print("Base de données initialisée.")

    return app