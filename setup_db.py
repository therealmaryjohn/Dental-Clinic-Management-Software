import sqlite3
import os
from database.db_config import DB_PATH

def setup_database():
    # Remove old DB if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Old database removed.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Patients table
    cursor.execute("""
        CREATE TABLE patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            contact TEXT,
            address TEXT
        )
    """)

    # Appointments table
    cursor.execute("""
        CREATE TABLE appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            reason TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
    """)

    # Treatments table
    cursor.execute("""
        CREATE TABLE treatments (
            treatment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cost REAL NOT NULL
        )
    """)

    # Billing table
    cursor.execute("""
        CREATE TABLE billing (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_name TEXT NOT NULL,
            total_amount REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
    """)

    # Inventory table
    cursor.execute("""
        CREATE TABLE inventory (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            threshold INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("Database created successfully at:", DB_PATH)

if __name__ == "__main__":
    setup_database()
