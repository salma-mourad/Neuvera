"""Pages publiques, accessibles sans connexion."""

from flask import Blueprint, render_template

bp = Blueprint("public", __name__)


@bp.route("/")
def home():
    return render_template("landing.html")