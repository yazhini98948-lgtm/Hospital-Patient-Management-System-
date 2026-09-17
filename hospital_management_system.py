import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
CORS(app)

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
# SEED INITIAL DATA
# ==============================================================================

def seed_database():
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
    print("[OK] Initial sample data seeded successfully.")


# ==============================================================================
# STATIC & FRONTEND ROUTES
# ==============================================================================


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hospital Management System</title>
    <!-- Bootstrap CSS CDN -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons CDN -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
    <style>
        /* ===== Custom Styles (Merged from style.css) ===== */
        :root {
            --app-primary: #2c6e8f;
            --app-primary-dark: #1b4b6b;
            --app-accent: #10b981;
            --app-accent-dark: #059669;
            --app-bg: #f3f6f9;
        }

        body {
            background-color: var(--app-bg);
            font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
            color: #2b2f32;
            min-height: 100vh;
        }

        /* Navbar */
        .app-navbar {
            background: linear-gradient(90deg, #1b4b6b 0%, #2c6e8f 100%);
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
        }

        .app-navbar .navbar-brand {
            font-size: 1.25rem;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        .app-navbar .nav-link {
            border-radius: 8px;
            padding: 0.5rem 0.9rem;
            transition: all 0.2s ease;
            color: rgba(255, 255, 255, 0.85);
            font-weight: 500;
        }

        .app-navbar .nav-link:hover {
            background-color: rgba(255, 255, 255, 0.15);
            color: #fff;
        }

        .app-navbar .nav-link.active {
            background-color: rgba(255, 255, 255, 0.25);
            color: #fff;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        }

        /* Stat cards */
        .stat-card {
            border: none;
            border-radius: 14px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .stat-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
        }

        .stat-icon {
            width: 52px;
            height: 52px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            flex-shrink: 0;
        }

        /* Cards */
        .card {
            border-radius: 14px;
            border: 1px solid rgba(0,0,0,0.06);
            overflow: hidden;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
        }

        .card-header {
            background-color: #fff;
            border-bottom: 1px solid #eef1f4;
            padding: 1rem 1.25rem;
        }

        /* Tables */
        .table-fixed {
            min-width: 700px;
        }

        .table thead th {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #6c757d;
            border-bottom-width: 1px;
            background-color: #fbfcfd;
            padding: 0.85rem 1rem;
        }

        .table tbody td {
            vertical-align: middle;
            font-size: 0.92rem;
            padding: 0.85rem 1rem;
        }

        .table-hover tbody tr:hover {
            background-color: #f8fafc;
        }

        /* Status badges */
        .badge {
            font-weight: 500;
            padding: 0.45em 0.75em;
        }

        .status-scheduled {
            background-color: #e7f1ff;
            color: #0d6efd;
            border: 1px solid #b6d4fe;
        }

        .status-completed {
            background-color: #d1fae5;
            color: #059669;
            border: 1px solid #a7f3d0;
        }

        .status-cancelled {
            background-color: #fde2e1;
            color: #dc2626;
            border: 1px solid #fecaca;
        }

        /* Empty state */
        .empty-state {
            text-align: center;
            padding: 3.5rem 1rem;
            color: #9aa5b1;
        }

        .empty-state i {
            font-size: 3rem;
            display: block;
            margin-bottom: 0.75rem;
            opacity: 0.7;
        }

        /* Buttons */
        .btn-icon {
            width: 34px;
            height: 34px;
            padding: 0;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            transition: all 0.15s ease-in-out;
        }

        .btn-primary {
            background-color: var(--app-primary);
            border-color: var(--app-primary);
        }

        .btn-primary:hover, .btn-primary:focus {
            background-color: var(--app-primary-dark);
            border-color: var(--app-primary-dark);
        }

        /* Form modal */
        .modal-content {
            border-radius: 14px;
            border: none;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        }

        .modal-header {
            border-bottom: 1px solid #eef1f4;
            padding: 1.25rem 1.5rem;
        }

        .modal-body {
            padding: 1.5rem;
        }

        .modal-footer {
            border-top: 1px solid #eef1f4;
            padding: 1rem 1.5rem;
        }

        /* Toast */
        .toast {
            border-radius: 10px;
            font-size: 0.9rem;
        }

        /* Search input focus */
        .input-group-text {
            border-right: none;
            background-color: #fff;
        }

        .input-group .form-control {
            border-left: none;
        }

        .input-group-text,
        .input-group .form-control:focus {
            border-color: #ced4da;
            box-shadow: none;
        }

        .input-group:focus-within {
            box-shadow: 0 0 0 0.25rem rgba(44, 110, 143, 0.15);
            border-radius: 0.375rem;
        }
        .input-group:focus-within .input-group-text,
        .input-group:focus-within .form-control {
            border-color: #86b7fe;
        }

        /* Mode Pill */
        .storage-pill {
            font-size: 0.75rem;
            padding: 0.25rem 0.65rem;
            border-radius: 20px;
            background-color: rgba(255, 255, 255, 0.2);
            color: #fff;
        }

        /* Responsive tweaks */
        @media (max-width: 768px) {
            .container-fluid {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }

            .stat-icon {
                width: 44px;
                height: 44px;
                font-size: 1.2rem;
            }

            .modal-dialog {
                margin: 0.5rem;
            }
        }
    </style>
</head>
<body>

    <!-- Header Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark app-navbar sticky-top mb-4">
        <div class="container-fluid px-4">
            <a class="navbar-brand d-flex align-items-center gap-2" href="#">
                <i class="bi bi-hospital fs-4 text-white"></i>
                <span>Hospital Management</span>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarContent" aria-controls="navbarContent" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarContent">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0 gap-1">
                    <li class="nav-item">
                        <a class="nav-link active" href="#" data-entity="dashboard">
                            <i class="bi bi-speedometer2 me-1"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#" data-entity="doctors">
                            <i class="bi bi-person-badge me-1"></i> Doctors
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#" data-entity="patients">
                            <i class="bi bi-people me-1"></i> Patients
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#" data-entity="appointments">
                            <i class="bi bi-calendar-check me-1"></i> Appointments
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#" data-entity="medical_records">
                            <i class="bi bi-clipboard2-pulse me-1"></i> Medical Records
                        </a>
                    </li>
                </ul>
                <div class="d-flex align-items-center gap-2">
                    <span id="storageModeBadge" class="storage-pill d-flex align-items-center gap-1">
                        <i class="bi bi-hdd-network"></i> <span id="storageModeText">Checking Mode...</span>
                    </span>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content Container -->
    <main class="container-fluid px-4 pb-5">

        <!-- VIEW: DASHBOARD -->
        <section id="view-dashboard" class="entity-view">
            <!-- Stat Cards -->
            <div class="row g-3 mb-4">
                <div class="col-12 col-sm-6 col-xl-3">
                    <div class="card stat-card p-3 bg-white">
                        <div class="d-flex align-items-center justify-content-between">
                            <div>
                                <span class="text-muted small fw-medium text-uppercase">Total Doctors</span>
                                <h2 class="mb-0 mt-1 fw-bold" id="stat-doctors">0</h2>
                            </div>
                            <div class="stat-icon bg-primary bg-opacity-10 text-primary">
                                <i class="bi bi-person-badge"></i>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-sm-6 col-xl-3">
                    <div class="card stat-card p-3 bg-white">
                        <div class="d-flex align-items-center justify-content-between">
                            <div>
                                <span class="text-muted small fw-medium text-uppercase">Total Patients</span>
                                <h2 class="mb-0 mt-1 fw-bold" id="stat-patients">0</h2>
                            </div>
                            <div class="stat-icon bg-success bg-opacity-10 text-success">
                                <i class="bi bi-people"></i>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-sm-6 col-xl-3">
                    <div class="card stat-card p-3 bg-white">
                        <div class="d-flex align-items-center justify-content-between">
                            <div>
                                <span class="text-muted small fw-medium text-uppercase">Appointments</span>
                                <h2 class="mb-0 mt-1 fw-bold" id="stat-appointments">0</h2>
                            </div>
                            <div class="stat-icon bg-info bg-opacity-10 text-info">
                                <i class="bi bi-calendar-check"></i>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-sm-6 col-xl-3">
                    <div class="card stat-card p-3 bg-white">
                        <div class="d-flex align-items-center justify-content-between">
                            <div>
                                <span class="text-muted small fw-medium text-uppercase">Medical Records</span>
                                <h2 class="mb-0 mt-1 fw-bold" id="stat-records">0</h2>
                            </div>
                            <div class="stat-icon bg-warning bg-opacity-10 text-warning">
                                <i class="bi bi-clipboard2-pulse"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Activity Tables -->
            <div class="row g-4">
                <div class="col-12 col-lg-7">
                    <div class="card bg-white h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="mb-0 fw-semibold text-secondary">
                                <i class="bi bi-calendar-event me-2 text-primary"></i>Upcoming Appointments
                            </h6>
                            <button class="btn btn-sm btn-outline-primary" onclick="switchView('appointments')">View All</button>
                        </div>
                        <div class="table-responsive">
                            <table class="table table-hover align-middle mb-0" id="dashboard-appointments">
                                <thead>
                                    <tr>
                                        <th>Patient</th>
                                        <th>Doctor</th>
                                        <th>Date</th>
                                        <th>Time</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr><td colspan="5" class="text-center text-muted py-4">Loading appointments...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-lg-5">
                    <div class="card bg-white h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="mb-0 fw-semibold text-secondary">
                                <i class="bi bi-journal-medical me-2 text-success"></i>Recent Medical Records
                            </h6>
                            <button class="btn btn-sm btn-outline-primary" onclick="switchView('medical_records')">View All</button>
                        </div>
                        <div class="table-responsive">
                            <table class="table table-hover align-middle mb-0" id="dashboard-records">
                                <thead>
                                    <tr>
                                        <th>Patient</th>
                                        <th>Diagnosis</th>
                                        <th>Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr><td colspan="3" class="text-center text-muted py-4">Loading records...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- VIEW: DOCTORS -->
        <section id="view-doctors" class="entity-view d-none">
            <div class="card bg-white">
                <div class="card-header d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-3">
                    <h5 class="mb-0 fw-semibold"><i class="bi bi-person-badge text-primary me-2"></i>Doctors</h5>
                    <div class="d-flex align-items-center gap-2">
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-search text-muted"></i></span>
                            <input type="text" id="search-doctors" class="form-control" placeholder="Search doctors...">
                        </div>
                        <button class="btn btn-primary text-nowrap" onclick="openEntityModal('doctors')">
                            <i class="bi bi-plus-lg me-1"></i> Add Doctor
                        </button>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0 table-fixed">
                        <thead>
                            <tr>
                                <th style="width: 70px;">ID</th>
                                <th>Name</th>
                                <th>Specialization</th>
                                <th>Phone</th>
                                <th>Email</th>
                                <th class="text-end" style="width: 120px;">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="table-doctors"></tbody>
                    </table>
                    <div id="empty-doctors" class="empty-state d-none">
                        <i class="bi bi-person-badge"></i>
                        <p class="mb-1 fw-medium">No doctors found</p>
                        <small class="text-muted">Click "Add Doctor" to create the first record.</small>
                    </div>
                </div>
            </div>
        </section>

        <!-- VIEW: PATIENTS -->
        <section id="view-patients" class="entity-view d-none">
            <div class="card bg-white">
                <div class="card-header d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-3">
                    <h5 class="mb-0 fw-semibold"><i class="bi bi-people text-success me-2"></i>Patients</h5>
                    <div class="d-flex align-items-center gap-2">
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-search text-muted"></i></span>
                            <input type="text" id="search-patients" class="form-control" placeholder="Search patients...">
                        </div>
                        <button class="btn btn-primary text-nowrap" onclick="openEntityModal('patients')">
                            <i class="bi bi-plus-lg me-1"></i> Add Patient
                        </button>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0 table-fixed">
                        <thead>
                            <tr>
                                <th style="width: 70px;">ID</th>
                                <th>Name</th>
                                <th>Age</th>
                                <th>Gender</th>
                                <th>Blood Group</th>
                                <th>Phone</th>
                                <th>City</th>
                                <th class="text-end" style="width: 120px;">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="table-patients"></tbody>
                    </table>
                    <div id="empty-patients" class="empty-state d-none">
                        <i class="bi bi-people"></i>
                        <p class="mb-1 fw-medium">No patients found</p>
                        <small class="text-muted">Click "Add Patient" to create the first record.</small>
                    </div>
                </div>
            </div>
        </section>

        <!-- VIEW: APPOINTMENTS -->
        <section id="view-appointments" class="entity-view d-none">
            <div class="card bg-white">
                <div class="card-header d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
                    <h5 class="mb-0 fw-semibold"><i class="bi bi-calendar-check text-info me-2"></i>Appointments</h5>
                    <div class="d-flex flex-wrap align-items-center gap-2">
                        <select id="filter-status" class="form-select" style="width: auto;">
                            <option value="">All Statuses</option>
                            <option value="Scheduled">Scheduled</option>
                            <option value="Completed">Completed</option>
                            <option value="Cancelled">Cancelled</option>
                        </select>
                        <div class="input-group" style="min-width: 200px;">
                            <span class="input-group-text"><i class="bi bi-search text-muted"></i></span>
                            <input type="text" id="search-appointments" class="form-control" placeholder="Search appointments...">
                        </div>
                        <button class="btn btn-primary text-nowrap" onclick="openEntityModal('appointments')">
                            <i class="bi bi-plus-lg me-1"></i> Add Appointment
                        </button>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0 table-fixed">
                        <thead>
                            <tr>
                                <th style="width: 70px;">ID</th>
                                <th>Patient</th>
                                <th>Doctor</th>
                                <th>Date</th>
                                <th>Time</th>
                                <th>Status</th>
                                <th class="text-end" style="width: 120px;">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="table-appointments"></tbody>
                    </table>
                    <div id="empty-appointments" class="empty-state d-none">
                        <i class="bi bi-calendar-x"></i>
                        <p class="mb-1 fw-medium">No appointments found</p>
                        <small class="text-muted">Click "Add Appointment" to schedule one.</small>
                    </div>
                </div>
            </div>
        </section>

        <!-- VIEW: MEDICAL RECORDS -->
        <section id="view-medical_records" class="entity-view d-none">
            <div class="card bg-white">
                <div class="card-header d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-3">
                    <h5 class="mb-0 fw-semibold"><i class="bi bi-clipboard2-pulse text-warning me-2"></i>Medical Records</h5>
                    <div class="d-flex align-items-center gap-2">
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-search text-muted"></i></span>
                            <input type="text" id="search-medical_records" class="form-control" placeholder="Search records...">
                        </div>
                        <button class="btn btn-primary text-nowrap" onclick="openEntityModal('medical_records')">
                            <i class="bi bi-plus-lg me-1"></i> Add Medical Record
                        </button>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0 table-fixed">
                        <thead>
                            <tr>
                                <th style="width: 70px;">ID</th>
                                <th>Patient</th>
                                <th>Diagnosis</th>
                                <th>Prescription</th>
                                <th>Date</th>
                                <th class="text-end" style="width: 120px;">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="table-medical_records"></tbody>
                    </table>
                    <div id="empty-medical_records" class="empty-state d-none">
                        <i class="bi bi-clipboard2-x"></i>
                        <p class="mb-1 fw-medium">No medical records found</p>
                        <small class="text-muted">Click "Add Medical Record" to add one.</small>
                    </div>
                </div>
            </div>
        </section>

    </main>

    <!-- Modal for Add / Edit Entity -->
    <div class="modal fade" id="entityModal" tabindex="-1" aria-labelledby="entityModalTitle" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <form id="entityForm" novalidate>
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title fw-semibold" id="entityModalTitle">Add/Edit Entity</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body" id="entityModalBody">
                        <!-- Form dynamic fields injected here -->
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
                        <button type="submit" class="btn btn-primary px-4">Save</button>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal for Delete Confirmation -->
    <div class="modal fade" id="deleteModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-semibold text-danger">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i>Confirm Deletion
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p id="deleteModalMessage" class="mb-0">Are you sure you want to delete this record? This action cannot be undone.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-danger px-4" id="confirmDeleteBtn">Delete</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Global Toast Notification -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 1100;">
        <div id="appToast" class="toast align-items-center text-white border-0 shadow-lg" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body d-flex align-items-center gap-2" id="appToastMessage"></div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    </div>

    <!-- Bootstrap 5.3.3 Bundle JS CDN -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Unified JavaScript Application Code -->
    <script>
        // ==========================================
        // 1. API & STORAGE LAYER
        // Supports Flask Backend (/api) with automatic
        // fallback to LocalStorage for standalone use!
        // ==========================================
        const API_URLS = {
            doctors: "/api/doctors",
            patients: "/api/patients",
            appointments: "/api/appointments",
            medical_records: "/api/medical-records",
        };

        const ENTITY_LABELS = {
            doctors: "Doctor",
            patients: "Patient",
            appointments: "Appointment",
            medical_records: "Medical Record",
        };

        const SPECIALIZATIONS = [
            "Cardiology", "Dermatology", "Neurology", "Orthopedics",
            "Pediatrics", "Psychiatry", "Gynecology", "Oncology",
            "Radiology", "General Medicine", "Ophthalmology", "Dentistry",
        ];

        const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"];

        // Seed data for standalone/local storage mode
        const DEFAULT_DATA = {
            doctors: [
                { id: 1, name: "Dr. Sarah Jenkins", specialization: "Cardiology", phone: "9876543210", email: "sarah.jenkins@hospital.com" },
                { id: 2, name: "Dr. Robert Chen", specialization: "Neurology", phone: "9876543211", email: "robert.chen@hospital.com" },
                { id: 3, name: "Dr. Priya Patel", specialization: "Pediatrics", phone: "9876543212", email: "priya.patel@hospital.com" },
                { id: 4, name: "Dr. James Wilson", specialization: "Orthopedics", phone: "9876543213", email: "james.wilson@hospital.com" }
            ],
            patients: [
                { id: 1, name: "Alice Johnson", age: 34, date_of_birth: "1990-05-14", gender: "Female", blood_group: "O+", phone: "9876500001", email: "alice.j@example.com", address: "123 Elm Street", city: "Chennai", emergency_contact_name: "Mark Johnson", emergency_contact_number: "9876500002" },
                { id: 2, name: "David Miller", age: 45, date_of_birth: "1979-11-20", gender: "Male", blood_group: "A+", phone: "9876500003", email: "david.m@example.com", address: "456 Oak Avenue", city: "Coimbatore", emergency_contact_name: "Lisa Miller", emergency_contact_number: "9876500004" },
                { id: 3, name: "Sophia Williams", age: 28, date_of_birth: "1996-03-08", gender: "Female", blood_group: "B+", phone: "9876500005", email: "sophia.w@example.com", address: "789 Pine Road", city: "Madurai", emergency_contact_name: "Emma Williams", emergency_contact_number: "9876500006" }
            ],
            appointments: [
                { id: 1, patient_id: 1, patient_name: "Alice Johnson", doctor_id: 1, doctor_name: "Dr. Sarah Jenkins", date: "2026-09-20", time: "10:30", status: "Scheduled", reason: "Annual cardiac checkup" },
                { id: 2, patient_id: 2, patient_name: "David Miller", doctor_id: 2, doctor_name: "Dr. Robert Chen", date: "2026-09-21", time: "14:00", status: "Scheduled", reason: "Migraine follow-up" },
                { id: 3, patient_id: 3, patient_name: "Sophia Williams", doctor_id: 3, doctor_name: "Dr. Priya Patel", date: "2026-09-15", time: "09:15", status: "Completed", reason: "Routine wellness visit" }
            ],
            medical_records: [
                { id: 1, patient_id: 1, patient_name: "Alice Johnson", diagnosis: "Mild Hypertension", prescription: "Amlodipine 5mg once daily", notes: "Patient advised to reduce sodium intake.", date: "2026-09-10" },
                { id: 2, patient_id: 2, patient_name: "David Miller", diagnosis: "Tension Headache", prescription: "Paracetamol 500mg as needed", notes: "Rest and hydration recommended.", date: "2026-09-12" }
            ]
        };

        // Local Storage Handler
        const LocalDB = {
            get(key) {
                const stored = localStorage.getItem("hms_" + key);
                if (!stored) {
                    localStorage.setItem("hms_" + key, JSON.stringify(DEFAULT_DATA[key] || []));
                    return DEFAULT_DATA[key] || [];
                }
                try {
                    return JSON.parse(stored);
                } catch(e) {
                    return DEFAULT_DATA[key] || [];
                }
            },
            set(key, data) {
                localStorage.setItem("hms_" + key, JSON.stringify(data));
            },
            getNextId(key) {
                const items = this.get(key);
                return items.reduce((max, item) => Math.max(max, item.id || 0), 0) + 1;
            }
        };

        // Unified API Controller
        const API = (() => {
            let useLocalFallback = false;

            async function checkBackend() {
                if (window.location.protocol === "file:") {
                    useLocalFallback = true;
                    updateModeIndicator("Local Storage Mode (File)");
                    return;
                }
                try {
                    const res = await fetch("/api/doctors", { method: "GET" });
                    if (res.ok) {
                        useLocalFallback = false;
                        updateModeIndicator("Connected to Backend Server");
                    } else {
                        useLocalFallback = true;
                        updateModeIndicator("Local Storage Mode");
                    }
                } catch (e) {
                    useLocalFallback = true;
                    updateModeIndicator("Local Storage Mode");
                }
            }

            function updateModeIndicator(text) {
                const badge = document.getElementById("storageModeBadge");
                const txt = document.getElementById("storageModeText");
                if (badge && txt) {
                    txt.textContent = text;
                    if (useLocalFallback) {
                        badge.classList.remove("bg-success");
                        badge.classList.add("bg-primary", "bg-opacity-50");
                    } else {
                        badge.classList.remove("bg-primary");
                        badge.classList.add("bg-success");
                    }
                }
            }

            async function request(url, method = "GET", body = null) {
                if (useLocalFallback) {
                    return mockRequest(url, method, body);
                }

                const options = {
                    method: method,
                    headers: { "Content-Type": "application/json" },
                };
                if (body) {
                    options.body = JSON.stringify(body);
                }
                let response;
                try {
                    response = await fetch(url, options);
                } catch (err) {
                    // Failover to local storage seamlessly
                    useLocalFallback = true;
                    updateModeIndicator("Local Storage Mode");
                    return mockRequest(url, method, body);
                }
                const data = await response.json().catch(() => ({}));
                if (!response.ok) {
                    const message = data.error || `Request failed (HTTP ${response.status})`;
                    throw new Error(message);
                }
                return data;
            }

            function getEntityKey(url) {
                if (url.includes("/api/doctors")) return "doctors";
                if (url.includes("/api/patients")) return "patients";
                if (url.includes("/api/appointments")) return "appointments";
                if (url.includes("/api/medical-records")) return "medical_records";
                return "doctors";
            }

            function mockRequest(url, method, body) {
                const entity = getEntityKey(url);
                const items = LocalDB.get(entity);
                const match = url.match(/\/(\d+)$/);
                const id = match ? parseInt(match[1], 10) : null;

                if (method === "GET") {
                    if (id !== null) {
                        const found = items.find(i => i.id === id);
                        if (!found) throw new Error("Record not found");
                        return found;
                    }
                    return items;
                } else if (method === "POST") {
                    const newId = LocalDB.getNextId(entity);
                    const newItem = { ...body, id: newId };
                    // Hydrate related names if appointment or medical record
                    if (entity === "appointments" || entity === "medical_records") {
                        const patients = LocalDB.get("patients");
                        const doctors = LocalDB.get("doctors");
                        if (newItem.patient_id) {
                            const p = patients.find(p => p.id == newItem.patient_id);
                            if (p) newItem.patient_name = p.name;
                        }
                        if (newItem.doctor_id) {
                            const d = doctors.find(d => d.id == newItem.doctor_id);
                            if (d) newItem.doctor_name = d.name;
                        }
                    }
                    items.push(newItem);
                    LocalDB.set(entity, items);
                    return newItem;
                } else if (method === "PUT") {
                    const index = items.findIndex(i => i.id === id);
                    if (index === -1) throw new Error("Record not found");
                    const updatedItem = { ...items[index], ...body, id };
                    if (entity === "appointments" || entity === "medical_records") {
                        const patients = LocalDB.get("patients");
                        const doctors = LocalDB.get("doctors");
                        if (updatedItem.patient_id) {
                            const p = patients.find(p => p.id == updatedItem.patient_id);
                            if (p) updatedItem.patient_name = p.name;
                        }
                        if (updatedItem.doctor_id) {
                            const d = doctors.find(d => d.id == updatedItem.doctor_id);
                            if (d) updatedItem.doctor_name = d.name;
                        }
                    }
                    items[index] = updatedItem;
                    LocalDB.set(entity, items);
                    return updatedItem;
                } else if (method === "DELETE") {
                    const filtered = items.filter(i => i.id !== id);
                    LocalDB.set(entity, filtered);
                    return { success: true };
                }
                return items;
            }

            return {
                checkBackend,
                list: (entity) => request(API_URLS[entity]),
                get: (url) => request(url),
                create: (url, body) => request(url, "POST", body),
                update: (url, body) => request(url, "PUT", body),
                remove: (url) => request(url, "DELETE"),
                search: (entity, term, status) => {
                    if (useLocalFallback) {
                        let list = LocalDB.get(entity);
                        if (term) {
                            const t = term.toLowerCase();
                            list = list.filter(item => {
                                return Object.values(item).some(v => String(v).toLowerCase().includes(t));
                            });
                        }
                        if (status && entity === "appointments") {
                            list = list.filter(item => item.status === status);
                        }
                        return Promise.resolve(list);
                    }
                    let base = entity === "medical_records" ? "/api/medical-records" : `/api/${entity}`;
                    const params = new URLSearchParams();
                    if (term) params.set("search", term);
                    if (status) params.set("status", status);
                    const qs = params.toString();
                    return request(qs ? `${base}?${qs}` : base);
                },
            };
        })();

        // ==========================================
        // 2. UI APPLICATION LOGIC (Merged from app.js)
        // ==========================================
        let currentView = "dashboard";
        let entityModal = null;
        let deleteModal = null;
        let toastEl = null;
        let currentForm = null;
        let pendingDelete = null;
        let dataCache = {};

        function escapeHtml(str) {
            if (str === undefined || str === null) return "";
            const div = document.createElement("div");
            div.textContent = String(str);
            return div.innerHTML;
        }

        function showToast(message, type = "success") {
            if (!toastEl) return;
            toastEl.classList.remove("text-bg-success", "text-bg-danger");
            toastEl.classList.add(type === "success" ? "text-bg-success" : "text-bg-danger");
            document.getElementById("appToastMessage").innerHTML = `
                <i class="bi ${type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'} fs-5"></i>
                <span>${escapeHtml(message)}</span>
            `;
            const toast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 3500 });
            toast.show();
        }

        // Initialize on page load
        document.addEventListener("DOMContentLoaded", async () => {
            toastEl = document.getElementById("appToast");
            entityModal = new bootstrap.Modal(document.getElementById("entityModal"));
            deleteModal = new bootstrap.Modal(document.getElementById("deleteModal"));

            await API.checkBackend();

            document.querySelectorAll(".nav-link[data-entity]").forEach((link) => {
                link.addEventListener("click", (e) => {
                    e.preventDefault();
                    switchView(link.dataset.entity);
                });
            });

            document.getElementById("entityForm").addEventListener("submit", onFormSubmit);
            document.getElementById("confirmDeleteBtn").addEventListener("click", onConfirmDelete);

            setupSearch("doctors");
            setupSearch("patients");
            setupSearch("appointments");
            setupSearch("medical_records");
            
            const filterStatus = document.getElementById("filter-status");
            if (filterStatus) {
                filterStatus.addEventListener("change", () => loadView("appointments"));
            }

            switchView("dashboard");
        });

        function switchView(view) {
            currentView = view;
            document.querySelectorAll(".entity-view").forEach((el) => el.classList.add("d-none"));
            const targetView = document.getElementById(`view-${view}`);
            if (targetView) targetView.classList.remove("d-none");

            document.querySelectorAll(".nav-link[data-entity]").forEach((link) => {
                link.classList.toggle("active", link.dataset.entity === view);
            });

            loadView(view);
        }

        async function loadView(view) {
            if (view === "dashboard") {
                loadDashboard();
                return;
            }
            const tbody = document.getElementById(`table-${view}`);
            if (tbody) {
                tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted py-4"><div class="spinner-border spinner-border-sm me-2 text-primary" role="status"></div>Loading records...</td></tr>`;
            }
            try {
                const searchInput = document.querySelector(`#search-${view}`);
                const term = searchInput ? searchInput.value.trim() : "";
                const statusSelect = document.getElementById("filter-status");
                const status = (view === "appointments" && statusSelect) ? statusSelect.value : "";
                const data = await API.search(view, term, status);
                dataCache[view] = data;
                renderTable(view, data);
            } catch (err) {
                renderTable(view, [], true);
                showToast(err.message, "danger");
            }
        }

        function setupSearch(view) {
            const input = document.querySelector(`#search-${view}`);
            if (!input) return;
            let timer = null;
            input.addEventListener("input", () => {
                clearTimeout(timer);
                timer = setTimeout(() => loadView(view), 350);
            });
        }

        // ---------- RENDERING ----------

        function renderTable(view, data, isError = false) {
            const tbody = document.getElementById(`table-${view}`);
            const emptyState = document.getElementById(`empty-${view}`);
            if (!tbody) return;

            tbody.innerHTML = "";
            if (!data || data.length === 0) {
                if (emptyState) {
                    if (isError) {
                        emptyState.querySelector("p").textContent = "Could not load data";
                        emptyState.querySelector("small").textContent = "Check that the server is running or storage is available.";
                    } else {
                        emptyState.querySelector("p").textContent = `No ${view.replace('_', ' ')} found`;
                        emptyState.querySelector("small").textContent =
                            `Click "Add ${ENTITY_LABELS[view]}" to create the first record.`;
                    }
                    emptyState.classList.remove("d-none");
                }
                return;
            }
            if (emptyState) emptyState.classList.add("d-none");

            data.forEach((item) => {
                tbody.insertAdjacentHTML("beforeend", buildRow(view, item));
            });
        }

        function buildRow(view, item) {
            switch (view) {
                case "doctors":
                    return `
                        <tr>
                            <td><span class="text-muted fw-semibold">#${item.id}</span></td>
                            <td><span class="fw-semibold text-dark">${escapeHtml(item.name)}</span></td>
                            <td><span class="badge text-bg-light border text-primary">${escapeHtml(item.specialization)}</span></td>
                            <td><i class="bi bi-telephone text-muted me-1 small"></i>${escapeHtml(item.phone)}</td>
                            <td><i class="bi bi-envelope text-muted me-1 small"></i>${escapeHtml(item.email)}</td>
                            <td class="text-end">
                                ${actionButtons("doctors", item.id)}
                            </td>
                        </tr>`;
                case "patients":
                    return `
                        <tr>
                            <td><span class="text-muted fw-semibold">#${item.id}</span></td>
                            <td><span class="fw-semibold text-dark">${escapeHtml(item.name)}</span></td>
                            <td>${item.age || "—"}</td>
                            <td>${escapeHtml(item.gender || "—")}</td>
                            <td>${bloodGroupBadge(item.blood_group)}</td>
                            <td><i class="bi bi-telephone text-muted me-1 small"></i>${escapeHtml(item.phone)}</td>
                            <td>${escapeHtml(item.city || "—")}</td>
                            <td class="text-end">
                                ${actionButtons("patients", item.id)}
                            </td>
                        </tr>`;
                case "appointments":
                    return `
                        <tr>
                            <td><span class="text-muted fw-semibold">#${item.id}</span></td>
                            <td><span class="fw-semibold text-dark">${escapeHtml(item.patient_name || `Patient #${item.patient_id}`)}</span></td>
                            <td><i class="bi bi-person-badge text-muted me-1 small"></i>${escapeHtml(item.doctor_name || `Doctor #${item.doctor_id}`)}</td>
                            <td><i class="bi bi-calendar3 text-muted me-1 small"></i>${escapeHtml(item.date)}</td>
                            <td><i class="bi bi-clock text-muted me-1 small"></i>${escapeHtml(item.time)}</td>
                            <td>${statusBadge(item.status)}</td>
                            <td class="text-end">
                                ${actionButtons("appointments", item.id)}
                            </td>
                        </tr>`;
                case "medical_records":
                    return `
                        <tr>
                            <td><span class="text-muted fw-semibold">#${item.id}</span></td>
                            <td><span class="fw-semibold text-dark">${escapeHtml(item.patient_name || `Patient #${item.patient_id}`)}</span></td>
                            <td><span class="badge bg-secondary bg-opacity-10 text-secondary border">${escapeHtml(item.diagnosis)}</span></td>
                            <td class="text-truncate" style="max-width: 220px;" title="${escapeHtml(item.prescription || '')}">${escapeHtml(item.prescription || "—")}</td>
                            <td><i class="bi bi-calendar3 text-muted me-1 small"></i>${escapeHtml(item.date)}</td>
                            <td class="text-end">
                                ${actionButtons("medical_records", item.id)}
                            </td>
                        </tr>`;
                default:
                    return "";
            }
        }

        function actionButtons(view, id) {
            return `
                <button class="btn btn-sm btn-outline-primary btn-icon me-1" onclick="editEntity('${view}', ${id})" title="Edit">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger btn-icon" onclick="askDelete('${view}', ${id})" title="Delete">
                    <i class="bi bi-trash"></i>
                </button>`;
        }

        function statusBadge(status) {
            const st = (status || "Scheduled").toLowerCase();
            const cls = `status-${st}`;
            return `<span class="badge ${cls}"><i class="bi bi-circle-fill me-1" style="font-size:0.5rem;"></i>${escapeHtml(status || "Scheduled")}</span>`;
        }

        function bloodGroupBadge(bg) {
            return `<span class="badge text-bg-danger bg-opacity-75 text-white">${escapeHtml(bg || "—")}</span>`;
        }

        // ---------- ADD / EDIT ----------

        function openEntityModal(view, item = null) {
            currentForm = { view, item };
            const title = item
                ? `Edit ${ENTITY_LABELS[view]}`
                : `Add New ${ENTITY_LABELS[view]}`;
            document.getElementById("entityModalTitle").textContent = title;
            document.querySelector("#entityModal .modal-footer .btn-primary").textContent = item ? "Update" : "Save";

            if (view === "appointments" || view === "medical_records") {
                buildSelectOptions(view).then(({ patients, doctors }) => {
                    const fields = buildFormFields(view, item, { patients, doctors });
                    document.getElementById("entityModalBody").innerHTML = fields;
                    entityModal.show();
                    wireFormEvents(view);
                });
            } else {
                document.getElementById("entityModalBody").innerHTML = buildFormFields(view, item);
                entityModal.show();
                wireFormEvents(view);
            }
        }

        function wireFormEvents(view) {
            if (view !== "patients") return;
            const dobInput = document.getElementById("f-date_of_birth");
            const ageInput = document.getElementById("f-age");
            if (!dobInput || !ageInput) return;
            const computeAge = () => {
                if (!dobInput.value) return;
                const dob = new Date(dobInput.value);
                if (isNaN(dob)) return;
                const now = new Date();
                let age = now.getFullYear() - dob.getFullYear();
                const m = now.getMonth() - dob.getMonth();
                if (m < 0 || (m === 0 && now.getDate() < dob.getDate())) age--;
                if (age >= 0 && age <= 150) ageInput.value = age;
            };
            dobInput.addEventListener("change", computeAge);
            dobInput.addEventListener("input", computeAge);
        }

        function buildFormFields(view, item, refs = null) {
            item = item || {};
            const val = (key, fallback = "") => (item[key] !== undefined && item[key] !== null ? item[key] : fallback);
            const today = new Date().toISOString().split("T")[0];

            switch (view) {
                case "doctors":
                    return `
                        ${textField("name", "Full Name", val("name"), "e.g. Dr. Jane Doe", true)}
                        <div class="mb-3">
                            <label class="form-label fw-medium">Specialization <span class="text-danger">*</span></label>
                            <select class="form-select" id="f-specialization" required>
                                <option value="">Select specialization</option>
                                ${SPECIALIZATIONS.map((s) => `<option value="${s}" ${val("specialization") === s ? "selected" : ""}>${s}</option>`).join("")}
                            </select>
                            <div class="invalid-feedback">Please select a specialization.</div>
                        </div>
                        ${textField("phone", "Phone", val("phone"), "e.g. 9876543210", true, "tel")}
                        ${textField("email", "Email", val("email"), "e.g. doctor@hospital.com", true, "email")}`;
                case "patients":
                    return `
                        ${textField("name", "Full Name", val("name"), "Enter patient's full name", true)}
                        <div class="row g-3">
                            <div class="col-sm-6">
                                ${textField("date_of_birth", "Date of Birth", val("date_of_birth"), "", false, "date")}
                            </div>
                            <div class="col-sm-6">
                                <div class="mb-3">
                                    <label class="form-label fw-medium">Age <span class="text-danger">*</span></label>
                                    <input type="number" class="form-control" id="f-age" min="0" max="150" value="${val("age")}" placeholder="Auto from DOB" required>
                                    <div class="invalid-feedback">Age must be between 0 and 150.</div>
                                </div>
                            </div>
                        </div>
                        <div class="row g-3">
                            <div class="col-sm-6">
                                <div class="mb-3">
                                    <label class="form-label fw-medium">Gender <span class="text-danger">*</span></label>
                                    <select class="form-select" id="f-gender" required>
                                        <option value="">Select gender</option>
                                        <option value="Male" ${val("gender") === "Male" ? "selected" : ""}>Male</option>
                                        <option value="Female" ${val("gender") === "Female" ? "selected" : ""}>Female</option>
                                        <option value="Other" ${val("gender") === "Other" ? "selected" : ""}>Other</option>
                                    </select>
                                    <div class="invalid-feedback">Please select a gender.</div>
                                </div>
                            </div>
                            <div class="col-sm-6">
                                <div class="mb-3">
                                    <label class="form-label fw-medium">Blood Group <span class="text-danger">*</span></label>
                                    <select class="form-select" id="f-blood_group" required>
                                        <option value="">Select blood group</option>
                                        ${BLOOD_GROUPS.map((bg) => `<option value="${bg}" ${val("blood_group") === bg ? "selected" : ""}>${bg}</option>`).join("")}
                                    </select>
                                    <div class="invalid-feedback">Please select a blood group.</div>
                                </div>
                            </div>
                        </div>
                        ${textField("phone", "Phone Number", val("phone"), "e.g. 9876543210", true, "tel")}
                        ${textField("email", "Email Address", val("email"), "e.g. patient@email.com", true, "email")}
                        <div class="mb-3">
                            <label class="form-label fw-medium">Address <span class="text-danger">*</span></label>
                            <textarea class="form-control" id="f-address" rows="2" placeholder="Enter complete residential address" required>${val("address")}</textarea>
                            <div class="invalid-feedback">Address is required.</div>
                        </div>
                        ${textField("city", "City", val("city"), "e.g. Chennai", true)}
                        <div class="row g-3">
                            <div class="col-sm-6">
                                ${textField("emergency_contact_name", "Emergency Contact Name", val("emergency_contact_name"), "e.g. John Doe", true)}
                            </div>
                            <div class="col-sm-6">
                                ${textField("emergency_contact_number", "Emergency Contact Number", val("emergency_contact_number"), "e.g. 9876501234", true, "tel")}
                            </div>
                        </div>`;
                case "appointments":
                    return `
                        <div class="mb-3">
                            <label class="form-label fw-medium">Patient <span class="text-danger">*</span></label>
                            <select class="form-select" id="f-patient_id" required>
                                <option value="">Select patient</option>
                                ${(refs?.patients || []).map((p) => `<option value="${p.id}" ${val("patient_id") == p.id ? "selected" : ""}>${escapeHtml(p.name)} (#${p.id})</option>`).join("")}
                            </select>
                            <div class="invalid-feedback">Please select a patient.</div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-medium">Doctor <span class="text-danger">*</span></label>
                            <select class="form-select" id="f-doctor_id" required>
                                <option value="">Select doctor</option>
                                ${(refs?.doctors || []).map((d) => `<option value="${d.id}" ${val("doctor_id") == d.id ? "selected" : ""}>${escapeHtml(d.name)} (${escapeHtml(d.specialization)})</option>`).join("")}
                            </select>
                            <div class="invalid-feedback">Please select a doctor.</div>
                        </div>
                        <div class="row g-3">
                            <div class="col-sm-7">
                                ${textField("date", "Date", val("date"), "", true, "date", { min: today })}
                            </div>
                            <div class="col-sm-5">
                                <div class="mb-3">
                                    <label class="form-label fw-medium">Time <span class="text-danger">*</span></label>
                                    <input type="time" class="form-control" id="f-time" value="${val("time")}" required>
                                    <div class="invalid-feedback">Time is required.</div>
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-medium">Status</label>
                            <select class="form-select" id="f-status">
                                <option value="Scheduled" ${val("status", "Scheduled") === "Scheduled" ? "selected" : ""}>Scheduled</option>
                                <option value="Completed" ${val("status") === "Completed" ? "selected" : ""}>Completed</option>
                                <option value="Cancelled" ${val("status") === "Cancelled" ? "selected" : ""}>Cancelled</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-medium">Reason for Visit</label>
                            <textarea class="form-control" id="f-reason" rows="2" placeholder="Reason for consultation (optional)">${val("reason")}</textarea>
                        </div>`;
                case "medical_records":
                    return `
                        <div class="mb-3">
                            <label class="form-label fw-medium">Patient <span class="text-danger">*</span></label>
                            <select class="form-select" id="f-patient_id" required>
                                <option value="">Select patient</option>
                                ${(refs?.patients || []).map((p) => `<option value="${p.id}" ${val("patient_id") == p.id ? "selected" : ""}>${escapeHtml(p.name)} (#${p.id})</option>`).join("")}
                            </select>
                            <div class="invalid-feedback">Please select a patient.</div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-medium">Diagnosis <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="f-diagnosis" value="${escapeHtml(val("diagnosis"))}" placeholder="e.g. Influenza, Hypertension" required>
                            <div class="invalid-feedback">Diagnosis is required.</div>
                        </div>
                        ${textField("date", "Record Date", val("date", today), "", true, "date", { max: today })}
                        <div class="mb-3">
                            <label class="form-label fw-medium">Prescription</label>
                            <textarea class="form-control" id="f-prescription" rows="2" placeholder="e.g. Paracetamol 500mg twice daily">${val("prescription")}</textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-medium">Clinical Notes</label>
                            <textarea class="form-control" id="f-notes" rows="2" placeholder="Additional observations and instructions">${val("notes")}</textarea>
                        </div>`;
                default:
                    return "";
            }
        }

        function textField(id, label, value, placeholder, required = false, type = "text", attrs = {}) {
            const extra = Object.entries(attrs)
                .map(([k, v]) => `${k}="${escapeHtml(v)}"`)
                .join(" ");
            return `
                <div class="mb-3">
                    <label class="form-label fw-medium">${label}${required ? ' <span class="text-danger">*</span>' : ""}</label>
                    <input type="${type}" class="form-control" id="f-${id}" value="${escapeHtml(value)}" placeholder="${placeholder}" ${required ? "required" : ""} ${extra}>
                    <div class="invalid-feedback">${label} is required.</div>
                </div>`;
        }

        async function buildSelectOptions(view) {
            const [patients, doctors] = await Promise.all([
                API.list("patients").catch(() => []),
                API.list("doctors").catch(() => []),
            ]);
            return { patients, doctors };
        }

        function editEntity(view, id) {
            const item = dataCache[view]?.find((r) => r.id === id);
            if (!item) {
                API.get(`${API_URLS[view]}/${id}`)
                    .then((data) => openEntityModal(view, data))
                    .catch((err) => showToast(err.message, "danger"));
                return;
            }
            openEntityModal(view, item);
        }

        async function onFormSubmit(e) {
            e.preventDefault();
            if (!currentForm) return;

            const form = e.target;
            if (!form.checkValidity()) {
                form.classList.add("was-validated");
                return;
            }
            form.classList.remove("was-validated");

            const { view, item } = currentForm;
            const id = item ? item.id : null;
            const url = id ? `${API_URLS[view]}/${id}` : API_URLS[view];

            try {
                const payload = buildPayload(view);
                if (id) {
                    await API.update(url, payload);
                    showToast(`${ENTITY_LABELS[view]} updated successfully`, "success");
                } else {
                    await API.create(url, payload);
                    showToast(`${ENTITY_LABELS[view]} added successfully`, "success");
                }
                entityModal.hide();
                form.reset();
                await loadView(view);
                if (view === "appointments" || view === "medical_records") loadDashboard();
            } catch (err) {
                showToast(err.message, "danger");
            }
        }

        function buildPayload(view) {
            const g = (vid) => {
                const el = document.getElementById(`f-${vid}`);
                return el ? el.value.trim() : "";
            };
            switch (view) {
                case "doctors":
                    return { 
                        name: g("name"), 
                        specialization: g("specialization"), 
                        phone: g("phone"), 
                        email: g("email") 
                    };
                case "patients":
                    return { 
                        name: g("name"), 
                        age: parseInt(g("age"), 10) || 0, 
                        date_of_birth: g("date_of_birth"), 
                        gender: g("gender"), 
                        blood_group: g("blood_group"), 
                        phone: g("phone"), 
                        email: g("email"), 
                        address: g("address"), 
                        city: g("city"), 
                        emergency_contact_name: g("emergency_contact_name"), 
                        emergency_contact_number: g("emergency_contact_number") 
                    };
                case "appointments":
                    return { 
                        patient_id: parseInt(g("patient_id"), 10), 
                        doctor_id: parseInt(g("doctor_id"), 10), 
                        date: g("date"), 
                        time: g("time"), 
                        status: g("status") || "Scheduled", 
                        reason: g("reason") 
                    };
                case "medical_records":
                    return { 
                        patient_id: parseInt(g("patient_id"), 10), 
                        diagnosis: g("diagnosis"), 
                        prescription: g("prescription"), 
                        notes: g("notes"), 
                        date: g("date") 
                    };
                default:
                    return {};
            }
        }

        // ---------- DELETE ----------

        function askDelete(view, id) {
            const item = dataCache[view]?.find((r) => r.id === id);
            const label = item
                ? item.name || item.patient_name || item.diagnosis || `#${id}`
                : `#${id}`;
            document.getElementById("deleteModalMessage").textContent =
                `Delete ${ENTITY_LABELS[view].toLowerCase()} "${label}"? This cannot be undone.`;
            pendingDelete = { view, id };
            deleteModal.show();
        }

        async function onConfirmDelete() {
            if (!pendingDelete) return;
            const { view, id } = pendingDelete;
            try {
                await API.remove(`${API_URLS[view]}/${id}`);
                showToast(`${ENTITY_LABELS[view]} deleted`, "success");
                deleteModal.hide();
                await loadView(view);
                loadDashboard();
            } catch (err) {
                showToast(err.message, "danger");
                deleteModal.hide();
            }
            pendingDelete = null;
        }

        // ---------- DASHBOARD ----------

        async function loadDashboard() {
            try {
                const [doctors, patients, appointments, records] = await Promise.all([
                    API.list("doctors").catch(() => []),
                    API.list("patients").catch(() => []),
                    API.list("appointments").catch(() => []),
                    API.list("medical_records").catch(() => []),
                ]);
                document.getElementById("stat-doctors").textContent = (doctors || []).length;
                document.getElementById("stat-patients").textContent = (patients || []).length;
                document.getElementById("stat-appointments").textContent = (appointments || []).length;
                document.getElementById("stat-records").textContent = (records || []).length;

                const sortedAppts = [...(appointments || [])]
                    .filter((a) => a.status === "Scheduled")
                    .sort((a, b) => ((a.date || "") + (a.time || "") < (b.date || "") + (b.time || "") ? -1 : 1));
                renderDashboardAppointments(sortedAppts.slice(0, 5));

                const sortedRecords = [...(records || [])].sort((a, b) => ((a.date || "") < (b.date || "") ? 1 : -1));
                renderDashboardRecords(sortedRecords.slice(0, 5));
            } catch (err) {
                showToast(err.message, "danger");
            }
        }

        function renderDashboardAppointments(appts) {
            const tbody = document.querySelector("#dashboard-appointments tbody");
            if (!tbody) return;
            if (appts.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-4"><i class="bi bi-calendar-check text-muted d-block mb-1 fs-4"></i>No upcoming appointments</td></tr>`;
                return;
            }
            tbody.innerHTML = appts
                .map(
                    (a) => `
                    <tr>
                        <td><span class="fw-semibold text-dark">${escapeHtml(a.patient_name || `Patient #${a.patient_id}`)}</span></td>
                        <td>${escapeHtml(a.doctor_name || `Doctor #${a.doctor_id}`)}</td>
                        <td><i class="bi bi-calendar3 text-muted me-1 small"></i>${escapeHtml(a.date)}</td>
                        <td><i class="bi bi-clock text-muted me-1 small"></i>${escapeHtml(a.time)}</td>
                        <td>${statusBadge(a.status)}</td>
                    </tr>`
                )
                .join("");
        }

        function renderDashboardRecords(records) {
            const tbody = document.querySelector("#dashboard-records tbody");
            if (!tbody) return;
            if (records.length === 0) {
                tbody.innerHTML = `<tr><td colspan="3" class="text-center text-muted py-4"><i class="bi bi-journal-medical text-muted d-block mb-1 fs-4"></i>No medical records yet</td></tr>`;
                return;
            }
            tbody.innerHTML = records
                .map(
                    (r) => `
                    <tr>
                        <td><span class="fw-semibold text-dark">${escapeHtml(r.patient_name || `Patient #${r.patient_id}`)}</span></td>
                        <td><span class="badge bg-secondary bg-opacity-10 text-secondary border">${escapeHtml(r.diagnosis)}</span></td>
                        <td><i class="bi bi-calendar3 text-muted me-1 small"></i>${escapeHtml(r.date)}</td>
                    </tr>`
                )
                .join("");
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return HTML_TEMPLATE



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

    doctor = Doctor(
        name=name,
        specialization=specialization,
        phone=phone,
        email=email,
    )
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
    date = data.get("date", "").strip() or datetime.utcnow().strftime("%Y-%m-%d")

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
# DASHBOARD STATS API (OPTIONAL HELPER)
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
# APP INITIALIZATION
# ==============================================================================

with app.app_context():
    db.create_all()
    seed_database()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[Hospital Management System] Backend running at: http://127.0.0.1:{port}/")
    app.run(host="0.0.0.0", port=port, debug=True)
