from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db_connection, init_db
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = 'hospital_management_secret_key'

init_db()

@app.route('/')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM doctors")
    total_doctors = cursor.fetchone()[0]
    
    today_str = date.today().isoformat()
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE appointment_date = ?", (today_str,))
    todays_appointments = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM resources WHERE is_available = 1")
    available_resources = cursor.fetchone()[0]
    
    conn.close()
    return render_template('dashboard.html', 
                           total_patients=total_patients, 
                           total_doctors=total_doctors, 
                           todays_appointments=todays_appointments, 
                           available_resources=available_resources)

@app.route('/patients', methods=['GET'])
def list_patients():
    search_query = request.args.get('search', '').strip()
    conn = get_db_connection()
    if search_query:
        patients = conn.execute(
            "SELECT * FROM patients WHERE name LIKE ? OR email LIKE ?", 
            (f'%{search_query}%', f'%{search_query}%')
        ).fetchall()
    else:
        patients = conn.execute("SELECT * FROM patients").fetchall()
    conn.close()
    return render_template('patient.html', patients=patients, search_query=search_query)

@app.route('/patients/add', methods=['POST'])
def add_patient():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    
    if not name or not email or not phone:
        flash("All fields are required to add a patient.", "danger")
        return redirect(url_for('list_patients'))
    
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO patients (name, email, phone) VALUES (?, ?, ?)", 
            (name, email, phone)
        )
        conn.commit()
        flash("Patient added successfully!", "success")
    except sqlite3.IntegrityError:
        flash("A patient with this email already exists.", "danger")
    finally:
        conn.close()
        
    return redirect(url_for('list_patients'))

@app.route('/patients/edit/<int:id>', methods=['POST'])
def edit_patient(id):
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    
    if not name or not email or not phone:
        flash("All fields are required to update a patient.", "danger")
        return redirect(url_for('list_patients'))
        
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE patients SET name = ?, email = ?, phone = ? WHERE id = ?",

if __name__ == '__main__':
    app.run(debug=True)