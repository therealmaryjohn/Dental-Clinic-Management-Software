import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QDateEdit
)
from PyQt5.QtCore import QDate
import os

DB_PATH = os.path.join(os.getcwd(), 'database', 'clinic.db')


class AppointmentsReport(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Appointments Report")
        self.setGeometry(300, 200, 800, 500)

        layout = QVBoxLayout()

        # Filter section
        filter_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())

        self.doctor_filter = QComboBox()
        self.doctor_filter.addItem("All")

        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.end_date)
        filter_layout.addWidget(QLabel("Doctor:"))
        filter_layout.addWidget(self.doctor_filter)

        self.load_button = QPushButton("Load Report")
        self.load_button.clicked.connect(self.load_report)
        filter_layout.addWidget(self.load_button)

        layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.populate_doctor_filter()

    def populate_doctor_filter(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT doctor FROM appointments")
        doctors = cursor.fetchall()
        for doctor in doctors:
            self.doctor_filter.addItem(doctor[0])
        conn.close()

    def load_report(self):
        from_date = self.start_date.date().toString("yyyy-MM-dd")
        to_date = self.end_date.date().toString("yyyy-MM-dd")
        selected_doctor = self.doctor_filter.currentText()

        query = """
            SELECT a.date, a.time, p.name, a.doctor, a.reason
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            WHERE date BETWEEN ? AND ?
        """
        params = [from_date, to_date]

        if selected_doctor != "All":
            query += " AND a.doctor = ?"
            params.append(selected_doctor)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Time", "Patient", "Doctor", "Reason"])

        for row_idx, row_data in enumerate(rows):
            for col_idx, item in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
