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

if __name__ == '__main__':
    app.run(debug=True)