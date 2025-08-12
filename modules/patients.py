from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem
)
import sqlite3

DB_PATH = "database/clinic.db"

class PatientsModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Patients")
        self.setMinimumSize(700, 500)

        self.name_input = QLineEdit()
        self.age_input = QLineEdit()
        self.gender_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.address_input = QLineEdit()
        self.medical_history_input = QLineEdit()

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Name:"))
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("Age:"))
        form_layout.addWidget(self.age_input)
        form_layout.addWidget(QLabel("Gender:"))
        form_layout.addWidget(self.gender_input)
        form_layout.addWidget(QLabel("Contact:"))
        form_layout.addWidget(self.contact_input)
        form_layout.addWidget(QLabel("Address:"))
        form_layout.addWidget(self.address_input)
        form_layout.addWidget(QLabel("Medical History:"))
        form_layout.addWidget(self.medical_history_input)

        self.add_button = QPushButton("Add Patient")
        self.add_button.clicked.connect(self.add_patient)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Gender", "Contact", "Address", "History"])
        self.table.cellClicked.connect(self.fill_form_from_table)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.add_button)
        layout.addWidget(self.table)
        layout.addWidget(self.delete_button)
        self.setLayout(layout)

        self.load_patients()

    def generate_patient_id(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM patients")
        count = cursor.fetchone()[0] + 1
        conn.close()
        return f"PAT{count:04d}"

    def add_patient(self):
        name = self.name_input.text()
        age = self.age_input.text()
        gender = self.gender_input.text()
        contact = self.contact_input.text()
        address = self.address_input.text()
        medical_history = self.medical_history_input.text()

        if not name:
            QMessageBox.warning(self, "Input Error", "Name is required.")
            return

        patient_id = self.generate_patient_id()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO patients (patient_id, name, age, gender, contact, address, medical_history)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (patient_id, name, age, gender, contact, address, medical_history))
            conn.commit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Patient ID already exists.")
        finally:
            conn.close()
            self.clear_inputs()
            self.load_patients()

    def load_patients(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT patient_id, name, age, gender, contact, address, medical_history FROM patients")
        records = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for row_num, row_data in enumerate(records):
            self.table.insertRow(row_num)
            for col_num, col_data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def fill_form_from_table(self, row):
        self.name_input.setText(self.table.item(row, 1).text())
        self.age_input.setText(self.table.item(row, 2).text())
        self.gender_input.setText(self.table.item(row, 3).text())
        self.contact_input.setText(self.table.item(row, 4).text())
        self.address_input.setText(self.table.item(row, 5).text())
        self.medical_history_input.setText(self.table.item(row, 6).text())

    def delete_selected(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No selection", "Please select a patient to delete.")
            return

        patient_id = self.table.item(selected_row, 0).text()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
        conn.commit()
        conn.close()

        self.load_patients()

    def clear_inputs(self):
        self.name_input.clear()
        self.age_input.clear()
        self.gender_input.clear()
        self.contact_input.clear()
        self.address_input.clear()
        self.medical_history_input.clear()
