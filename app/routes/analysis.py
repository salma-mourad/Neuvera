"""Dépôt d'un fichier EEG, analyse et affichage du rapport."""

from pathlib import Path

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import services
from app.extensions import db
from app.models import AnalysisReport, Recording
from app.routes.patients import get_own_patient

bp = Blueprint("analysis", __name__)

SUSPICION_LEVELS = ["Faible", "Modéré", "Élevé"]


@bp.route("/patients/<int:patient_id>/analyse", methods=["GET", "POST"])
@login_required
def upload(patient_id):
    patient = get_own_patient(patient_id)

    if request.method == "POST":
        file = request.files.get("eeg_file")
        suspicion = request.form.get("suspicion_level", "")

        if not file or not file.filename or not services.is_allowed(file.filename):
            flash("Choisissez un fichier .edf.", "error")
            return render_template("upload.html", patient=patient, levels=SUSPICION_LEVELS)
        if suspicion not in SUSPICION_LEVELS:
            flash("Choisissez un niveau de suspicion.", "error")
            return render_template("upload.html", patient=patient, levels=SUSPICION_LEVELS)

        upload_dir = Path(current_app.config["UPLOAD_DIR"])
        stored_name = services.save_upload(file, upload_dir)
        try:
            result = services.analyze_file(upload_dir / stored_name)
        except ValueError as e:
            (upload_dir / stored_name).unlink(missing_ok=True)
            flash(f"Fichier refusé : {e}", "error")
            return render_template("upload.html", patient=patient, levels=SUSPICION_LEVELS)

        recording = Recording(
            patient=patient,
            original_name=file.filename,
            stored_name=stored_name,
            suspicion_level=suspicion,
            family_history=request.form.get("family_history") == "oui",
            symptoms=request.form.get("symptoms", "").strip(),
            notes=request.form.get("notes", "").strip(),
        )
        recording.report = AnalysisReport(**result)
        db.session.add(recording)
        db.session.commit()
        return redirect(url_for("analysis.report", recording_id=recording.id))

    return render_template("upload.html", patient=patient, levels=SUSPICION_LEVELS)


@bp.route("/analyses/<int:recording_id>")
@login_required
def report(recording_id):
    recording = db.session.get(Recording, recording_id)
    if recording is None or recording.patient.user_id != current_user.id:
        abort(404)
    return render_template("report.html", recording=recording, report=recording.report)