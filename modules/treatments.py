from functools import partial

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
import sqlite3

DB_PATH = "database/clinic.db"

class TreatmentsModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Treatments")
        self.setMinimumSize(600, 400)

        self.name_input = QLineEdit()
        self.cost_input = QLineEdit()
        self.add_button = QPushButton("Add Treatment")
        self.add_button.clicked.connect(self.add_treatment)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Treatment", "Cost", "Actions"])
        self.table.cellDoubleClicked.connect(self.load_selected_treatment)

        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.update_treatment)
        self.update_button.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Treatment Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Cost:"))
        layout.addWidget(self.cost_input)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.update_button)
        layout.addLayout(buttons_layout)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.selected_treatment_id = None
        self.load_treatments()

    def add_treatment(self):
        name = self.name_input.text().strip()
        try:
            cost = float(self.cost_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid", "Please enter a valid cost.")
            return

        if not name:
            QMessageBox.warning(self, "Missing", "Please enter a treatment name.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO treatments (name, cost) VALUES (?, ?)", (name, cost))
        conn.commit()
        conn.close()

        self.name_input.clear()
        self.cost_input.clear()
        self.load_treatments()

    def load_treatments(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, cost FROM treatments")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for row_num, (tid, name, cost) in enumerate(rows):
            self.table.insertRow(row_num)
            self.table.setItem(row_num, 0, QTableWidgetItem(name))
            self.table.setItem(row_num, 1, QTableWidgetItem(f"{cost:.2f}"))
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(partial(self.delete_treatment, tid))
            self.table.setCellWidget(row_num, 2, delete_button)

    def delete_treatment(self, treatment_id):
        reply = QMessageBox.question(self, "Delete", "Are you sure?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM treatments WHERE id = ?", (treatment_id,))
            conn.commit()
            conn.close()
            self.load_treatments()

    def load_selected_treatment(self, row, column):
        self.selected_treatment_id = self.get_treatment_id_by_row(row)
        self.name_input.setText(self.table.item(row, 0).text())
        self.cost_input.setText(self.table.item(row, 1).text())
        self.add_button.setVisible(False)
        self.update_button.setVisible(True)

    def update_treatment(self):
        name = self.name_input.text().strip()
        try:
            cost = float(self.cost_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid", "Please enter a valid cost.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE treatments SET name = ?, cost = ? WHERE id = ?",
            (name, cost, self.selected_treatment_id)
        )
        conn.commit()
        conn.close()

        self.clear_form()
        self.load_treatments()

    def clear_form(self):
        self.name_input.clear()
        self.cost_input.clear()
        self.selected_treatment_id = None
        self.add_button.setVisible(True)
        self.update_button.setVisible(False)

    def get_treatment_id_by_row(self, row):
        name = self.table.item(row, 0).text()
        cost = float(self.table.item(row, 1).text())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM treatments WHERE name = ? AND cost = ?", (name, cost))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
