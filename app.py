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
            (name, email, phone, id)
        )
        conn.commit()
        flash("Patient updated successfully!", "success")
    except sqlite3.IntegrityError:
        flash("A patient with this email already exists.", "danger")
    finally:
        conn.close()
        
    return redirect(url_for('list_patients'))

@app.route('/patients/delete/<int:id>', methods=['POST'])
def delete_patient(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM patients WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Patient deleted successfully!", "warning")
    return redirect(url_for('list_patients'))

@app.route('/doctors', methods=['GET'])
def list_doctors():
    search_query = request.args.get('search', '').strip()
    conn = get_db_connection()
    if search_query:
        doctors = conn.execute(
            "SELECT * FROM doctors WHERE name LIKE ? OR specialty LIKE ?", 
            (f'%{search_query}%', f'%{search_query}%')
        ).fetchall()
    else:
        doctors = conn.execute("SELECT * FROM doctors").fetchall()
    conn.close()
    return render_template('doctor.html', doctors=doctors, search_query=search_query)

@app.route('/doctors/add', methods=['POST'])
def add_doctor():
    name = request.form.get('name', '').strip()
    specialty = request.form.get('specialty', '').strip()
    fee_str = request.form.get('consultation_fee', '').strip()
    
    if not name or not specialty or not fee_str:
        flash("All fields are required to add a doctor.", "danger")
        return redirect(url_for('list_doctors'))
        
    try:
        fee = float(fee_str)
        if fee < 0:
            raise ValueError
    except ValueError:
        flash("Consultation fee must be a valid non-negative number.", "danger")
        return redirect(url_for('list_doctors'))
        
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO doctors (name, specialty, consultation_fee) VALUES (?, ?, ?)",
        (name, specialty, fee)
    )
    conn.commit()
    conn.close()
    flash("Doctor added successfully!", "success")
    return redirect(url_for('list_doctors'))

@app.route('/doctors/edit/<int:id>', methods=['POST'])
def edit_doctor(id):
    name = request.form.get('name', '').strip()
    specialty = request.form.get('specialty', '').strip()
    fee_str = request.form.get('consultation_fee', '').strip()
    
    if not name or not specialty or not fee_str:
        flash("All fields are required to update a doctor.", "danger")
        return redirect(url_for('list_doctors'))
        
    try:
        fee = float(fee_str)
        if fee < 0:
            raise ValueError
    except ValueError:
        flash("Consultation fee must be a valid non-negative number.", "danger")
        return redirect(url_for('list_doctors'))
        
    conn = get_db_connection()
    conn.execute(
        "UPDATE doctors SET name = ?, specialty = ?, consultation_fee = ? WHERE id = ?",
        (name, specialty, fee, id)
    )
    conn.commit()
    conn.close()
    flash("Doctor updated successfully!", "success")
    return redirect(url_for('list_doctors'))

@app.route('/doctors/delete/<int:id>', methods=['POST'])
def delete_doctor(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM doctors WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Doctor deleted successfully!", "warning")
    return redirect(url_for('list_doctors'))

@app.route('/appointments', methods=['GET'])
def list_appointments():
    conn = get_db_connection()
    appointments = conn.execute("""
        SELECT a.id, p.name as patient_name, d.name as doctor_name, d.specialty,
               a.appointment_date, a.appointment_time, a.status, a.diagnosis,
               r.name as resource_name, r.type as resource_type
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        LEFT JOIN resources r ON a.resource_id = r.id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
    """).fetchall()
    
    patients = conn.execute("SELECT id, name FROM patients").fetchall()
    doctors = conn.execute("SELECT id, name, specialty FROM doctors").fetchall()
    conn.close()
    return render_template('appointment.html', 
                           appointments=appointments, 
                           patients=patients, 
                           doctors=doctors)

@app.route('/appointments/book', methods=['POST'])
def book_appointment():
    patient_id = request.form.get('patient_id')
    doctor_id = request.form.get('doctor_id')
    app_date = request.form.get('appointment_date')
    app_time = request.form.get('appointment_time')
    resource_type = request.form.get('resource_type')
    
    if not patient_id or not doctor_id or not app_date or not app_time or not resource_type:
        flash("All booking details are required.", "danger")
        return redirect(url_for('list_appointments'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM patients WHERE id = ?", (patient_id,))
        if not cursor.fetchone():
            flash("Error: Selected patient does not exist.", "danger")
            return redirect(url_for('list_appointments'))
            
        cursor.execute("SELECT id FROM doctors WHERE id = ?", (doctor_id,))
        if not cursor.fetchone():
            flash("Error: Selected doctor does not exist.", "danger")
            return redirect(url_for('list_appointments'))
            
        cursor.execute(
            "SELECT id FROM appointments WHERE doctor_id = ? AND appointment_date = ? AND appointment_time = ? AND status != 'Cancelled'",
            (doctor_id, app_date, app_time)
        )
        if cursor.fetchone():
            flash("Error: Doctor already has an active appointment at this date and time.", "danger")
            return redirect(url_for('list_appointments'))
            
        cursor.execute(
            "SELECT id, name FROM resources WHERE type = ? AND is_available = 1 LIMIT 1",
            (resource_type,)
        )
        resource = cursor.fetchone()
        if not resource:
            flash(f"Error: No available '{resource_type}' resource to allocate. Booking rejected.", "danger")
            return redirect(url_for('list_appointments'))
            
        resource_id = resource['id']
        cursor.execute("UPDATE resources SET is_available = 0 WHERE id = ?", (resource_id,))
        
        cursor.execute(
            "INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, resource_id, status) VALUES (?, ?, ?, ?, ?, 'Scheduled')",
            (patient_id, doctor_id, app_date, app_time, resource_id)
        )
        conn.commit()
        flash(f"Appointment booked successfully! Allocated: {resource['name']}", "success")
    except sqlite3.Error as e:
        pass
        flash(f"Database error during transaction: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for('list_appointments'))

@app.route('/appointments/complete/<int:id>', methods=['POST'])
def complete_appointment(id):
    diagnosis = request.form.get('diagnosis', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT resource_id FROM appointments WHERE id = ?", (id,))
        appointment = cursor.fetchone()
        if not appointment:
            flash("Appointment not found.", "danger")
            return redirect(url_for('list_appointments'))
            
        resource_id = appointment['resource_id']

if __name__ == '__main__':
    app.run(debug=True)