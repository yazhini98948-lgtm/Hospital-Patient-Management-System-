import json
import unittest
from app import app, db, Doctor, Patient, Appointment, MedicalRecord

class HospitalManagementSystemBackendTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            from app import seed_database
            seed_database()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_doctors(self):
        response = self.client.get("/api/doctors")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(len(data) >= 4)
        self.assertEqual(data[0]["name"], "Dr. Sarah Jenkins")

    def test_search_doctors(self):
        response = self.client.get("/api/doctors?search=Cardiology")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["specialization"], "Cardiology")

    def test_create_update_delete_doctor(self):
        # Create
        new_doc = {
            "name": "Dr. Gregory House",
            "specialization": "Diagnostic Medicine",
            "phone": "9998887776",
            "email": "house@princetonplainsboro.org"
        }
        res = self.client.post("/api/doctors", json=new_doc)
        self.assertEqual(res.status_code, 201)
        doc_id = res.get_json()["id"]

        # Get Single
        res_get = self.client.get(f"/api/doctors/{doc_id}")
        self.assertEqual(res_get.status_code, 200)
        self.assertEqual(res_get.get_json()["name"], "Dr. Gregory House")

        # Update
        res_up = self.client.put(f"/api/doctors/{doc_id}", json={"specialization": "Nephrology"})
        self.assertEqual(res_up.status_code, 200)
        self.assertEqual(res_up.get_json()["specialization"], "Nephrology")

        # Delete
        res_del = self.client.delete(f"/api/doctors/{doc_id}")
        self.assertEqual(res_del.status_code, 200)

        # Confirm deleted
        res_check = self.client.get(f"/api/doctors/{doc_id}")
        self.assertEqual(res_check.status_code, 404)

    def test_patients_crud(self):
        # Create Patient
        new_patient = {
            "name": "Emily Watson",
            "age": 29,
            "date_of_birth": "1997-02-14",
            "gender": "Female",
            "blood_group": "AB+",
            "phone": "9123456780",
            "email": "emily.w@example.com",
            "address": "42 Beacon St",
            "city": "Boston",
            "emergency_contact_name": "Tom Watson",
            "emergency_contact_number": "9123456789"
        }
        res = self.client.post("/api/patients", json=new_patient)
        self.assertEqual(res.status_code, 201)
        patient_id = res.get_json()["id"]

        # Search Patient
        res_search = self.client.get("/api/patients?search=Boston")
        self.assertEqual(res_search.status_code, 200)
        self.assertEqual(len(res_search.get_json()), 1)

        # Update Patient
        res_up = self.client.put(f"/api/patients/{patient_id}", json={"city": "Cambridge"})
        self.assertEqual(res_up.status_code, 200)
        self.assertEqual(res_up.get_json()["city"], "Cambridge")

        # Delete Patient
        res_del = self.client.delete(f"/api/patients/{patient_id}")
        self.assertEqual(res_del.status_code, 200)

    def test_appointments_crud_and_filter(self):
        # List appointments
        res = self.client.get("/api/appointments")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(len(data) >= 3)
        self.assertIn("patient_name", data[0])
        self.assertIn("doctor_name", data[0])

        # Filter by status
        res_scheduled = self.client.get("/api/appointments?status=Scheduled")
        self.assertEqual(res_scheduled.status_code, 200)
        for appt in res_scheduled.get_json():
            self.assertEqual(appt["status"], "Scheduled")

        # Create appointment
        new_appt = {
            "patient_id": 1,
            "doctor_id": 2,
            "date": "2026-09-25",
            "time": "11:00",
            "status": "Scheduled",
            "reason": "Follow-up scan review"
        }
        res_post = self.client.post("/api/appointments", json=new_appt)
        self.assertEqual(res_post.status_code, 201)
        appt_id = res_post.get_json()["id"]
        self.assertEqual(res_post.get_json()["patient_name"], "Alice Johnson")
        self.assertEqual(res_post.get_json()["doctor_name"], "Dr. Robert Chen")

        # Update status
        res_up = self.client.put(f"/api/appointments/{appt_id}", json={"status": "Completed"})
        self.assertEqual(res_up.status_code, 200)
        self.assertEqual(res_up.get_json()["status"], "Completed")

        # Delete
        res_del = self.client.delete(f"/api/appointments/{appt_id}")
        self.assertEqual(res_del.status_code, 200)

    def test_medical_records_crud(self):
        # List medical records
        res = self.client.get("/api/medical-records")
        self.assertEqual(res.status_code, 200)
        records = res.get_json()
        self.assertTrue(len(records) >= 2)
        self.assertIn("patient_name", records[0])

        # Create record
        new_rec = {
            "patient_id": 3,
            "diagnosis": "Seasonal Allergy",
            "prescription": "Cetirizine 10mg once daily",
            "notes": "Follow-up if symptoms persist for 2 weeks",
            "date": "2026-09-17"
        }
        res_post = self.client.post("/api/medical-records", json=new_rec)
        self.assertEqual(res_post.status_code, 201)
        rec_id = res_post.get_json()["id"]
        self.assertEqual(res_post.get_json()["patient_name"], "Sophia Williams")

        # Update record
        res_up = self.client.put(f"/api/medical-records/{rec_id}", json={"notes": "Symptoms resolved"})
        self.assertEqual(res_up.status_code, 200)
        self.assertEqual(res_up.get_json()["notes"], "Symptoms resolved")

        # Delete record
        res_del = self.client.delete(f"/api/medical-records/{rec_id}")
        self.assertEqual(res_del.status_code, 200)

    def test_dashboard_stats(self):
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        stats = res.get_json()
        self.assertIn("doctors_count", stats)
        self.assertIn("patients_count", stats)
        self.assertIn("appointments_count", stats)
        self.assertIn("records_count", stats)

    def test_static_index_serving(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Hospital Management System", res.data)

if __name__ == "__main__":
    unittest.main()
