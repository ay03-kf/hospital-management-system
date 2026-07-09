# V Care Hospital - Resource & Appointment Management System

A web application designed for hospital resource tracking, appointment scheduling, and billing management. This project focuses on database design, relations, and transactions.

## Features
- **Patient & Doctor Management**: Add, edit, search, and delete profiles for patients and doctors.
- **Resource Allocation**: When booking an appointment, the system automatically allocates the first available resource of the required type (Consultation Room, ECG Unit, X-Ray Room, or Ventilator) using a database transaction.
- **Double Booking Prevention**: Checks to ensure a doctor does not have another active appointment at the same date and time.
- **Billing Summary**: Automatically generates a bill combining the doctor's fee and resource usage cost upon checkup completion.
- **Admin Dashboard**: Shows real-time statistics including appointments count per doctor and resource usage count using SQL aggregation queries.

## Architecture & Tech Stack
- **Backend**: Python, Flask, raw SQLite3
- **Frontend**: HTML5, Bootstrap 5, Custom CSS

## Database Schema
The SQLite database contains the following tables:
- `patients`: Patient registry (ID, name, email, phone).
- `doctors`: Doctor details (ID, name, specialty, fee).
- `resources`: Hospital rooms and medical equipment tracking.
- `appointments`: Booking schedules mapping patients, doctors, and allocated resources.

## Local Installation
1. Install Flask:
   ```bash
   pip install flask
   ```
2. Run the application:
   ```bash
   python app.py
   ```
3. Open in your browser: `http://127.0.0.1:5000/`
