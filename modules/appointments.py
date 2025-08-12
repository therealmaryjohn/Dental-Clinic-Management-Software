from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, \
    QFormLayout, QHBoxLayout, QComboBox, QMessageBox, QDateEdit, QTimeEdit
from PyQt5.QtCore import Qt
import sqlite3
from database.db_config import DB_PATH
from PyQt5.QtCore import QDate, QTime

from utils.refresh_utils import refresh_module


# def showEvent(self, event):
#     super().showEvent(event)
#     refresh_module(self)

class AppointmentsModule(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Form to add appointments
        form_layout = QFormLayout()

        self.patient_combo = QComboBox()
        self.load_patients()
        form_layout.addRow("Patient:", self.patient_combo)

        # self.doctor_combo = QComboBox()
        # self.doctor_combo.addItems(["Neethu Mathew"])  # You can extend this
        # form_layout.addRow("Doctor:", self.doctor_combo)
        self.doctor_input = QLineEdit()
        self.doctor_input.setText("Neethu Mathew")  # Pre-fill default doctor
        form_layout.addRow("Doctor:", self.doctor_input)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)  # Show calendar popup
        self.date_input.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_input)

        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        form_layout.addRow("Time:", self.time_input)

        self.reason_input = QLineEdit()
        form_layout.addRow("Reason:", self.reason_input)

        self.add_button = QPushButton("Add Appointment")
        self.add_button.clicked.connect(self.add_appointment)
        form_layout.addWidget(self.add_button)

        layout.addLayout(form_layout)

        # Table to show appointments
        self.appointments_table = QTableWidget()
        self.appointments_table.setColumnCount(6)
        self.appointments_table.setHorizontalHeaderLabels(["ID", "Patient", "Doctor", "Date", "Time", "Reason"])
        layout.addWidget(QLabel("Appointments:"))
        layout.addWidget(self.appointments_table)

        self.setLayout(layout)
        self.load_appointments()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_patients()  # Reload patients every time tab is shown

    def load_patients(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT patient_id, name, address  FROM patients")
        patients = cursor.fetchall()
        self.patient_combo.clear()
        for pid, name, add in patients:
            self.patient_combo.addItem(f"{name} (ID:{pid}) {add}", pid)
        conn.close()

    def add_appointment(self):
        patient_id = self.patient_combo.currentData()
        # doctor = self.doctor_combo.currentText()
        doctor = self.doctor_input.text().strip()
        date = self.date_input.text()
        time = self.time_input.text()
        reason = self.reason_input.text()

        if not all([patient_id, doctor, date, time, reason]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO appointments (patient_id, doctor, date, time, reason)
            VALUES (?, ?, ?, ?, ?)
        """, (patient_id, doctor, date, time, reason))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Appointment added successfully.")
        self.load_appointments()

    def load_appointments(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.appointment_id, p.name, a.doctor, a.date, a.time, a.reason
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
        """)
        appointments = cursor.fetchall()
        self.appointments_table.setRowCount(0)

        for row_idx, row_data in enumerate(appointments):
            self.appointments_table.insertRow(row_idx)
            for col_idx, col_data in enumerate(row_data):
                self.appointments_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

        conn.close()
