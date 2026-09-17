"""
==============================================================================
Hospital Management System - Complete Backend API Server
==============================================================================
Framework: Flask + Flask-SQLAlchemy + SQLite + Flask-CORS
Database: SQLite (hospital.db)

Endpoints:
- Doctors:         GET, POST, PUT, DELETE  --> /api/doctors, /api/doctors/<id>
- Patients:        GET, POST, PUT, DELETE  --> /api/patients, /api/patients/<id>
- Appointments:    GET, POST, PUT, DELETE  --> /api/appointments, /api/appointments/<id>
- Medical Records: GET, POST, PUT, DELETE  --> /api/medical-records, /api/medical-records/<id>
- Stats Summary:   GET                     --> /api/stats
- Web Interface:   GET                     --> /
==============================================================================
"""

import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
CORS(app)  # Enable Cross-Origin Resource Sharing for all origins

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'hospital.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSON_SORT_KEYS"] = False

db = SQLAlchemy(app)

# ==============================================================================
# DATABASE MODELS
# ==============================================================================

class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    appointments = db.relationship("Appointment", backref="doctor", cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "specialization": self.specialization,
            "phone": self.phone,
            "email": self.email,
        }


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    date_of_birth = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(20), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(80), nullable=False)
    emergency_contact_name = db.Column(db.String(120), nullable=False)
    emergency_contact_number = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    appointments = db.relationship("Appointment", backref="patient", cascade="all, delete-orphan", lazy=True)
    medical_records = db.relationship("MedicalRecord", backref="patient", cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender,
            "blood_group": self.blood_group,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "city": self.city,
            "emergency_contact_name": self.emergency_contact_name,
            "emergency_contact_number": self.emergency_contact_number,
        }


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), default="Scheduled", nullable=False)
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "patient_name": self.patient.name if self.patient else f"Patient #{self.patient_id}",
            "doctor_id": self.doctor_id,
            "doctor_name": self.doctor.name if self.doctor else f"Doctor #{self.doctor_id}",
            "date": self.date,
            "time": self.time,
            "status": self.status,
            "reason": self.reason or "",
        }


class MedicalRecord(db.Model):
    __tablename__ = "medical_records"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    diagnosis = db.Column(db.String(255), nullable=False)
    prescription = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    date = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "patient_name": self.patient.name if self.patient else f"Patient #{self.patient_id}",
            "diagnosis": self.diagnosis,
            "prescription": self.prescription or "",
            "notes": self.notes or "",
            "date": self.date,
        }


# ==============================================================================
# SAMPLE DATA SEEDER
# ==============================================================================

def seed_database():
    """Seed initial demo data if database tables are empty."""
    if Doctor.query.first() is not None:
        return

    doctors = [
        Doctor(name="Dr. Sarah Jenkins", specialization="Cardiology", phone="9876543210", email="sarah.jenkins@hospital.com"),
        Doctor(name="Dr. Robert Chen", specialization="Neurology", phone="9876543211", email="robert.chen@hospital.com"),
        Doctor(name="Dr. Priya Patel", specialization="Pediatrics", phone="9876543212", email="priya.patel@hospital.com"),
        Doctor(name="Dr. James Wilson", specialization="Orthopedics", phone="9876543213", email="james.wilson@hospital.com"),
    ]
    db.session.add_all(doctors)
    db.session.commit()

    patients = [
        Patient(name="Alice Johnson", age=34, date_of_birth="1990-05-14", gender="Female", blood_group="O+", phone="9876500001", email="alice.j@example.com", address="123 Elm Street", city="Chennai", emergency_contact_name="Mark Johnson", emergency_contact_number="9876500002"),
        Patient(name="David Miller", age=45, date_of_birth="1979-11-20", gender="Male", blood_group="A+", phone="9876500003", email="david.m@example.com", address="456 Oak Avenue", city="Coimbatore", emergency_contact_name="Lisa Miller", emergency_contact_number="9876500004"),
        Patient(name="Sophia Williams", age=28, date_of_birth="1996-03-08", gender="Female", blood_group="B+", phone="9876500005", email="sophia.w@example.com", address="789 Pine Road", city="Madurai", emergency_contact_name="Emma Williams", emergency_contact_number="9876500006"),
    ]
    db.session.add_all(patients)
    db.session.commit()

    appointments = [
        Appointment(patient_id=1, doctor_id=1, date="2026-09-20", time="10:30", status="Scheduled", reason="Annual cardiac checkup"),
        Appointment(patient_id=2, doctor_id=2, date="2026-09-21", time="14:00", status="Scheduled", reason="Migraine follow-up"),
        Appointment(patient_id=3, doctor_id=3, date="2026-09-15", time="09:15", status="Completed", reason="Routine wellness visit"),
    ]
    db.session.add_all(appointments)
    db.session.commit()

    records = [
        MedicalRecord(patient_id=1, diagnosis="Mild Hypertension", prescription="Amlodipine 5mg once daily", notes="Patient advised to reduce sodium intake.", date="2026-09-10"),
        MedicalRecord(patient_id=2, diagnosis="Tension Headache", prescription="Paracetamol 500mg as needed", notes="Rest and hydration recommended.", date="2026-09-12"),
    ]
    db.session.add_all(records)
    db.session.commit()
    print("[OK] Database seeded with initial sample data.")


# ==============================================================================
# WEB & STATIC SERVING
# ==============================================================================

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


# ==============================================================================
# DOCTORS API
# ==============================================================================

@app.route("/api/doctors", methods=["GET"])
def get_doctors():
    search = request.args.get("search", "").strip()
    query = Doctor.query
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Doctor.name.ilike(search_pattern),
                Doctor.specialization.ilike(search_pattern),
                Doctor.phone.ilike(search_pattern),
                Doctor.email.ilike(search_pattern),
            )
        )
    doctors = query.order_by(Doctor.id.asc()).all()
    return jsonify([d.to_dict() for d in doctors])


@app.route("/api/doctors/<int:doctor_id>", methods=["GET"])
def get_doctor(doctor_id):
    doctor = db.session.get(Doctor, doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404
    return jsonify(doctor.to_dict())


@app.route("/api/doctors", methods=["POST"])
def create_doctor():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    specialization = data.get("specialization", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()

    if not name or not specialization or not phone or not email:
        return jsonify({"error": "Name, specialization, phone, and email are required"}), 400

    doctor = Doctor(name=name, specialization=specialization, phone=phone, email=email)
    db.session.add(doctor)
    db.session.commit()
    return jsonify(doctor.to_dict()), 201


@app.route("/api/doctors/<int:doctor_id>", methods=["PUT"])
def update_doctor(doctor_id):
    doctor = db.session.get(Doctor, doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    data = request.get_json() or {}
    if "name" in data and data["name"].strip():
        doctor.name = data["name"].strip()
    if "specialization" in data and data["specialization"].strip():
        doctor.specialization = data["specialization"].strip()
    if "phone" in data and data["phone"].strip():
        doctor.phone = data["phone"].strip()
    if "email" in data and data["email"].strip():
        doctor.email = data["email"].strip()

    db.session.commit()
    return jsonify(doctor.to_dict())


@app.route("/api/doctors/<int:doctor_id>", methods=["DELETE"])
def delete_doctor(doctor_id):
    doctor = db.session.get(Doctor, doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    db.session.delete(doctor)
    db.session.commit()
    return jsonify({"message": "Doctor deleted successfully", "success": True})


# ==============================================================================
# PATIENTS API
# ==============================================================================

@app.route("/api/patients", methods=["GET"])
def get_patients():
    search = request.args.get("search", "").strip()
    query = Patient.query
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Patient.name.ilike(search_pattern),
                Patient.phone.ilike(search_pattern),
                Patient.email.ilike(search_pattern),
                Patient.city.ilike(search_pattern),
                Patient.blood_group.ilike(search_pattern),
                Patient.emergency_contact_name.ilike(search_pattern),
                Patient.emergency_contact_number.ilike(search_pattern),
            )
        )
    patients = query.order_by(Patient.id.asc()).all()
    return jsonify([p.to_dict() for p in patients])


@app.route("/api/patients/<int:patient_id>", methods=["GET"])
def get_patient(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify(patient.to_dict())


@app.route("/api/patients", methods=["POST"])
def create_patient():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    gender = data.get("gender", "").strip()
    blood_group = data.get("blood_group", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    address = data.get("address", "").strip()
    city = data.get("city", "").strip()
    emergency_contact_name = data.get("emergency_contact_name", "").strip()
    emergency_contact_number = data.get("emergency_contact_number", "").strip()
    
    try:
        age = int(data.get("age", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Valid age is required"}), 400

    date_of_birth = data.get("date_of_birth", "")

    if not name or not gender or not blood_group or not phone or not email or not address or not city:
        return jsonify({"error": "All required patient fields must be provided"}), 400

    patient = Patient(
        name=name,
        age=age,
        date_of_birth=date_of_birth,
        gender=gender,
        blood_group=blood_group,
        phone=phone,
        email=email,
        address=address,
        city=city,
        emergency_contact_name=emergency_contact_name,
        emergency_contact_number=emergency_contact_number,
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify(patient.to_dict()), 201


@app.route("/api/patients/<int:patient_id>", methods=["PUT"])
def update_patient(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    data = request.get_json() or {}
    if "name" in data and data["name"].strip():
        patient.name = data["name"].strip()
    if "age" in data:
        try:
            patient.age = int(data["age"])
        except (ValueError, TypeError):
            pass
    if "date_of_birth" in data:
        patient.date_of_birth = data["date_of_birth"]
    if "gender" in data and data["gender"].strip():
        patient.gender = data["gender"].strip()
    if "blood_group" in data and data["blood_group"].strip():
        patient.blood_group = data["blood_group"].strip()
    if "phone" in data and data["phone"].strip():
        patient.phone = data["phone"].strip()
    if "email" in data and data["email"].strip():
        patient.email = data["email"].strip()
    if "address" in data and data["address"].strip():
        patient.address = data["address"].strip()
    if "city" in data and data["city"].strip():
        patient.city = data["city"].strip()
    if "emergency_contact_name" in data:
        patient.emergency_contact_name = data["emergency_contact_name"].strip()
    if "emergency_contact_number" in data:
        patient.emergency_contact_number = data["emergency_contact_number"].strip()

    db.session.commit()
    return jsonify(patient.to_dict())


@app.route("/api/patients/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    db.session.delete(patient)
    db.session.commit()
    return jsonify({"message": "Patient deleted successfully", "success": True})


# ==============================================================================
# APPOINTMENTS API
# ==============================================================================

@app.route("/api/appointments", methods=["GET"])
def get_appointments():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = db.session.query(Appointment).join(Patient, Appointment.patient_id == Patient.id).join(Doctor, Appointment.doctor_id == Doctor.id)

    if status:
        query = query.filter(Appointment.status == status)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Patient.name.ilike(search_pattern),
                Doctor.name.ilike(search_pattern),
                Appointment.reason.ilike(search_pattern),
                Appointment.date.ilike(search_pattern),
                Appointment.time.ilike(search_pattern),
            )
        )

    appointments = query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return jsonify([a.to_dict() for a in appointments])


@app.route("/api/appointments/<int:appointment_id>", methods=["GET"])
def get_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404
    return jsonify(appointment.to_dict())


@app.route("/api/appointments", methods=["POST"])
def create_appointment():
    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    doctor_id = data.get("doctor_id")
    date = data.get("date", "").strip()
    time = data.get("time", "").strip()
    status = data.get("status", "Scheduled").strip() or "Scheduled"
    reason = data.get("reason", "").strip()

    if not patient_id or not doctor_id or not date or not time:
        return jsonify({"error": "Patient, Doctor, Date, and Time are required"}), 400

    try:
        patient_id = int(patient_id)
        doctor_id = int(doctor_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid patient or doctor ID"}), 400

    patient = db.session.get(Patient, patient_id)
    doctor = db.session.get(Doctor, doctor_id)
    if not patient or not doctor:
        return jsonify({"error": "Referenced patient or doctor does not exist"}), 400

    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        date=date,
        time=time,
        status=status,
        reason=reason,
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify(appointment.to_dict()), 201


@app.route("/api/appointments/<int:appointment_id>", methods=["PUT"])
def update_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    data = request.get_json() or {}
    if "patient_id" in data and data["patient_id"]:
        patient = db.session.get(Patient, int(data["patient_id"]))
        if not patient:
            return jsonify({"error": "Referenced patient does not exist"}), 400
        appointment.patient_id = int(data["patient_id"])

    if "doctor_id" in data and data["doctor_id"]:
        doctor = db.session.get(Doctor, int(data["doctor_id"]))
        if not doctor:
            return jsonify({"error": "Referenced doctor does not exist"}), 400
        appointment.doctor_id = int(data["doctor_id"])

    if "date" in data and data["date"].strip():
        appointment.date = data["date"].strip()
    if "time" in data and data["time"].strip():
        appointment.time = data["time"].strip()
    if "status" in data and data["status"].strip():
        appointment.status = data["status"].strip()
    if "reason" in data:
        appointment.reason = data["reason"].strip()

    db.session.commit()
    return jsonify(appointment.to_dict())


@app.route("/api/appointments/<int:appointment_id>", methods=["DELETE"])
def delete_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    db.session.delete(appointment)
    db.session.commit()
    return jsonify({"message": "Appointment deleted successfully", "success": True})


# ==============================================================================
# MEDICAL RECORDS API
# ==============================================================================

@app.route("/api/medical-records", methods=["GET"])
def get_medical_records():
    search = request.args.get("search", "").strip()

    query = db.session.query(MedicalRecord).join(Patient, MedicalRecord.patient_id == Patient.id)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Patient.name.ilike(search_pattern),
                MedicalRecord.diagnosis.ilike(search_pattern),
                MedicalRecord.prescription.ilike(search_pattern),
                MedicalRecord.notes.ilike(search_pattern),
                MedicalRecord.date.ilike(search_pattern),
            )
        )

    records = query.order_by(MedicalRecord.date.desc(), MedicalRecord.id.desc()).all()
    return jsonify([r.to_dict() for r in records])


@app.route("/api/medical-records/<int:record_id>", methods=["GET"])
def get_medical_record(record_id):
    record = db.session.get(MedicalRecord, record_id)
    if not record:
        return jsonify({"error": "Medical record not found"}), 404
    return jsonify(record.to_dict())


@app.route("/api/medical-records", methods=["POST"])
def create_medical_record():
    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    diagnosis = data.get("diagnosis", "").strip()
    prescription = data.get("prescription", "").strip()
    notes = data.get("notes", "").strip()
    date = data.get("date", "").strip() or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if not patient_id or not diagnosis:
        return jsonify({"error": "Patient and Diagnosis are required"}), 400

    try:
        patient_id = int(patient_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid patient ID"}), 400

    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({"error": "Referenced patient does not exist"}), 400

    record = MedicalRecord(
        patient_id=patient_id,
        diagnosis=diagnosis,
        prescription=prescription,
        notes=notes,
        date=date,
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@app.route("/api/medical-records/<int:record_id>", methods=["PUT"])
def update_medical_record(record_id):
    record = db.session.get(MedicalRecord, record_id)
    if not record:
        return jsonify({"error": "Medical record not found"}), 404

    data = request.get_json() or {}
    if "patient_id" in data and data["patient_id"]:
        patient = db.session.get(Patient, int(data["patient_id"]))
        if not patient:
            return jsonify({"error": "Referenced patient does not exist"}), 400
        record.patient_id = int(data["patient_id"])

    if "diagnosis" in data and data["diagnosis"].strip():
        record.diagnosis = data["diagnosis"].strip()
    if "prescription" in data:
        record.prescription = data["prescription"].strip()
    if "notes" in data:
        record.notes = data["notes"].strip()
    if "date" in data and data["date"].strip():
        record.date = data["date"].strip()

    db.session.commit()
    return jsonify(record.to_dict())


@app.route("/api/medical-records/<int:record_id>", methods=["DELETE"])
def delete_medical_record(record_id):
    record = db.session.get(MedicalRecord, record_id)
    if not record:
        return jsonify({"error": "Medical record not found"}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "Medical record deleted successfully", "success": True})


# ==============================================================================
# DASHBOARD STATS API
# ==============================================================================

@app.route("/api/stats", methods=["GET"])
def get_stats():
    return jsonify({
        "doctors_count": Doctor.query.count(),
        "patients_count": Patient.query.count(),
        "appointments_count": Appointment.query.count(),
        "records_count": MedicalRecord.query.count(),
    })


@app.route("/<path:filename>")
def static_files(filename):
    if filename.startswith("api/"):
        return jsonify({"error": "Endpoint not found"}), 404
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.isfile(file_path):
        return send_from_directory(BASE_DIR, filename)
    return send_from_directory(BASE_DIR, "index.html")


# ==============================================================================
# INITIALIZATION & ENTRY POINT
# ==============================================================================

with app.app_context():
    db.create_all()
    seed_database()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[Hospital Management System] Backend running at: http://127.0.0.1:{port}/")
    app.run(host="0.0.0.0", port=port, debug=True)
