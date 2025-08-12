import sys
import os
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QAction
)
from modules.patients import PatientsModule
from modules.appointments import AppointmentsModule
from modules.billing import BillingModule
from modules.treatments import TreatmentsModule
from modules.inventory import InventoryModule
from modules.reports import ReportsModule  # Unified Reports tab
from modules.reports_billing import BillingReport
from modules.reports_inventory import InventoryReport
import os
print("Current working dir:", os.getcwd())
print("Database path being used:", os.path.join(os.getcwd(), 'database', 'clinic.db'))


# Database path
DB_PATH = os.path.join(os.getcwd(), 'database', 'clinic.db')



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dr. N's Dental Studio")
        self.setGeometry(200, 100, 1000, 600)

        self.setup_database()

        # === Menu Bar ===
        menu_bar = self.menuBar()
        reports_menu = menu_bar.addMenu("Reports")

        # Billing Report
        billing_report_action = QAction("Billing Report", self)
        billing_report_action.triggered.connect(self.open_billing_report)
        reports_menu.addAction(billing_report_action)

        # Inventory Report
        inventory_report_action = QAction("Inventory Report", self)
        inventory_report_action.triggered.connect(self.open_inventory_report)
        reports_menu.addAction(inventory_report_action)

        # === Tabbed Layout (Main Modules) ===
        self.tabs = QTabWidget()
        self.tabs.addTab(PatientsModule(), "Patients")
        self.tabs.addTab(AppointmentsModule(), "Appointments")
        self.tabs.addTab(BillingModule(), "Billing")
        self.tabs.addTab(TreatmentsModule(), "Treatments")
        self.tabs.addTab(InventoryModule(), "Inventory")
        self.tabs.addTab(ReportsModule(), "Reports")  # All reports inside here

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        container.setLayout(layout)
        self.setCentralWidget(container)


    def open_billing_report(self):
        self.billing_report_window = BillingReport()
        self.billing_report_window.show()

    def open_inventory_report(self):
        self.inventory_report_window = InventoryReport()
        self.inventory_report_window.show()

    def setup_database(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # === Patients table ===
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT UNIQUE,
            name TEXT,
            age INTEGER,
            gender TEXT,
            contact TEXT,
            address TEXT
            -- medical_history column will be added below if missing
        )
        """)
        # Add missing column if not exists
        cursor.execute("PRAGMA table_info(patients)")
        columns = [col[1] for col in cursor.fetchall()]
        if "medical_history" not in columns:
            cursor.execute("ALTER TABLE patients ADD COLUMN medical_history TEXT")

        # === Appointments table ===
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            doctor TEXT,
            date TEXT,
            time TEXT,
            reason TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
        """)

        # === Billing table ===
        # Billing table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                doctor_name TEXT,
                treatment TEXT,
                total_amount REAL,
                payment_status TEXT,
                date TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
            )
            """)

        # === Treatments table ===
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS treatments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            cost REAL
        )
        """)

        # === Inventory table ===
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            quantity INTEGER,
            threshold INTEGER
        )
        """)

        conn.commit()
        conn.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Load and apply the custom stylesheet
    style_file = os.path.join(os.getcwd(), "Support", "style.qss")
    try:
        with open(style_file, "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print("Could not load stylesheet:", e)

    # Create folders if they don't exist
    os.makedirs("database", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    os.makedirs("settings", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    os.makedirs("modules", exist_ok=True)
    os.makedirs("ui", exist_ok=True)
    os.makedirs("utils", exist_ok=True)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
