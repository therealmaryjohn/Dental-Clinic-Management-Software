import sqlite3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QDateEdit, QComboBox, QTableWidget, QTableWidgetItem, QHBoxLayout
from PyQt5.QtCore import Qt, QDate
from database.db_config import DB_PATH

class BillingReport(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Billing Report")
        self.resize(800, 500)

        layout = QVBoxLayout()

        # Filters
        filter_layout = QHBoxLayout()
        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setDate(QDate.currentDate())

        self.doctor_combo = QComboBox()
        self.doctor_combo.addItem("All Doctors")
        self.load_doctors()

        self.patient_combo = QComboBox()
        self.patient_combo.addItem("All Patients")
        self.load_patients()

        self.filter_button = QPushButton("Filter")
        self.filter_button.clicked.connect(self.load_data)

        for widget in [QLabel("From:"), self.start_date, QLabel("To:"), self.end_date,
                       QLabel("Doctor:"), self.doctor_combo, QLabel("Patient:"), self.patient_combo,
                       self.filter_button]:
            filter_layout.addWidget(widget)

        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Patient", "Doctor", "Treatment", "Amount"])
        layout.addWidget(self.table)

        self.total_label = QLabel("Total Revenue: ₹0.00")
        layout.addWidget(self.total_label)

        self.setLayout(layout)
        self.load_data()

    def load_doctors(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT doctor FROM bills")
        doctors = [row[0] for row in cursor.fetchall()]
        self.doctor_combo.addItems(doctors)
        conn.close()

    def load_patients(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT patient_name FROM bills")
        patients = [row[0] for row in cursor.fetchall()]
        self.patient_combo.addItems(patients)
        conn.close()

    def load_data(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = "SELECT date, patient_name, doctor, treatment, amount FROM bills WHERE date BETWEEN ? AND ?"
        params = [self.start_date.date().toString("yyyy-MM-dd"),
                  self.end_date.date().toString("yyyy-MM-dd")]

        if self.doctor_combo.currentText() != "All Doctors":
            query += " AND doctor = ?"
            params.append(self.doctor_combo.currentText())

        if self.patient_combo.currentText() != "All Patients":
            query += " AND patient_name = ?"
            params.append(self.patient_combo.currentText())

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        total = 0
        for row_idx, row_data in enumerate(rows):
            self.table.insertRow(row_idx)
            for col_idx, col_data in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
            total += float(row_data[-1])

        self.total_label.setText(f"Total Revenue: ₹{total:.2f}")
