import sqlite3
import os

DATABASE_PATH = 'hospital.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    schema_exists = os.path.exists(DATABASE_PATH)
    conn = get_db_connection()
    
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM doctors")
    if cursor.fetchone()[0] == 0:
        doctors_data = [
            ("Dr. Ramkishan Yadav", "Paediatrician", 500.0),
            ("Dr. Vandana Yadav", "Anesthesiology", 600.0),
            ("Dr. Hitesh Yadav", "Cardiologist", 800.0),
            ("Dr. Shivam Yadav", "Nephrologist", 700.0)
        ]
        cursor.executemany(
            "INSERT INTO doctors (name, specialty, consultation_fee) VALUES (?, ?, ?)",
            doctors_data
        )

        resources_data = [
            ("OPD Room 101", "Consultation Room", 200.0, 1),
            ("OPD Room 102", "Consultation Room", 200.0, 1),
            ("ECG Unit", "ECG Machine", 300.0, 1),
            ("X-Ray Room", "X-Ray Room", 500.0, 1),
            ("ICU Bed 01", "Ventilator", 1500.0, 1)
        ]
        cursor.executemany(
            "INSERT INTO resources (name, type, cost_per_use, is_available) VALUES (?, ?, ?, ?)",
            resources_data
        )

        patients_data = [
            ("Pooja Katiyar", "pooja.k@example.com", "98765-43210"),
            ("Rahul Patel", "rahul.p@example.com", "98270-12345"),
            ("Nidhi Gupta", "nidhi.g@example.com", "94250-98765"),
            ("Kushagra Agarwal", "kushagra.a@example.com", "90090-11223")
        ]
        cursor.executemany(
            "INSERT INTO patients (name, email, phone) VALUES (?, ?, ?)",
            patients_data
        )

        conn.commit()
    conn.close()

