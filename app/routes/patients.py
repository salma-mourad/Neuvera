"""Gestion des patients du médecin connecté."""

from datetime import date
from pathlib import Path

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Patient

bp = Blueprint("patients", __name__, url_prefix="/patients")


def get_own_patient(patient_id):
    """Renvoie le patient s'il appartient au médecin connecté, sinon 404."""
    patient = db.session.get(Patient, patient_id)
    if patient is None or patient.user_id != current_user.id:
        abort(404)
    return patient


@bp.route("/")
@login_required
def list_patients():
    patients = Patient.query.filter_by(user_id=current_user.id).order_by(Patient.last_name).all()
    return render_template("patients.html", patients=patients)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_patient():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        sex = request.form.get("sex", "")
        try:
            birth_date = date.fromisoformat(request.form.get("birth_date", ""))
        except ValueError:
            birth_date = None

        if not first_name or not last_name or sex not in {"F", "M"} or birth_date is None:
            flash("Tous les champs sont obligatoires.", "error")
        elif birth_date > date.today():
            flash("La date de naissance ne peut pas être dans le futur.", "error")
        else:
            patient = Patient(first_name=first_name, last_name=last_name, sex=sex,
                              birth_date=birth_date, user_id=current_user.id)
            db.session.add(patient)
            db.session.commit()
            flash("Patient ajouté.", "success")
            return redirect(url_for("patients.detail", patient_id=patient.id))

    return render_template("patient_form.html")


@bp.route("/<int:patient_id>")
@login_required
def detail(patient_id):
    return render_template("patient_detail.html", patient=get_own_patient(patient_id))


@bp.route("/<int:patient_id>/delete", methods=["POST"])
@login_required
def delete(patient_id):
    patient = get_own_patient(patient_id)
    upload_dir = Path(current_app.config["UPLOAD_DIR"])
    for recording in patient.recordings:
        (upload_dir / recording.stored_name).unlink(missing_ok=True)
    db.session.delete(patient)
    db.session.commit()
    flash("Patient supprimé.", "success")
    return redirect(url_for("patients.list_patients"))