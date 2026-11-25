"""Tableau de bord : chiffres clés du médecin connecté."""

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.models import AnalysisReport, Patient, Recording

bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard")
@login_required
def index():
    reports = (
        AnalysisReport.query.join(Recording).join(Patient)
        .filter(Patient.user_id == current_user.id)
        .order_by(AnalysisReport.created_at.desc())
    )
    stats = {
        "patients": Patient.query.filter_by(user_id=current_user.id).count(),
        "analyses": reports.count(),
        "positifs": reports.filter(AnalysisReport.label == 1).count(),
    }
    return render_template("dashboard.html", stats=stats, recent=reports.limit(5).all())