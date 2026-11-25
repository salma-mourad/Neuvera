"""Tables de la base de données."""

from datetime import date, datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


def _now():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=_now)

    patients = db.relationship("Patient", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=_now)

    user = db.relationship("User", back_populates="patients")
    recordings = db.relationship(
        "Recording", back_populates="patient", cascade="all, delete-orphan",
        order_by="Recording.uploaded_at.desc()",
    )

    @property
    def age(self):
        today = date.today()
        b = self.birth_date
        return today.year - b.year - ((today.month, today.day) < (b.month, b.day))

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Recording(db.Model):
    """Un fichier EEG déposé, avec l'état clinique du patient au même moment."""

    __tablename__ = "recordings"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=_now)

    suspicion_level = db.Column(db.String(20), nullable=False)
    family_history = db.Column(db.Boolean, default=False)
    symptoms = db.Column(db.Text)
    notes = db.Column(db.Text)

    patient = db.relationship("Patient", back_populates="recordings")
    report = db.relationship("AnalysisReport", back_populates="recording", uselist=False,
                             cascade="all, delete-orphan")


class AnalysisReport(db.Model):
    __tablename__ = "analysis_reports"

    id = db.Column(db.Integer, primary_key=True)
    recording_id = db.Column(db.Integer, db.ForeignKey("recordings.id"), unique=True, nullable=False)
    n_epochs = db.Column(db.Integer, nullable=False)
    proba_logistic = db.Column(db.Float, nullable=False)
    proba_cnn = db.Column(db.Float)
    proba_final = db.Column(db.Float, nullable=False)
    label = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=_now)

    recording = db.relationship("Recording", back_populates="report")

    @property
    def label_text(self):
        return "Profil compatible avec une schizophrénie" if self.label == 1 else "Profil sain"