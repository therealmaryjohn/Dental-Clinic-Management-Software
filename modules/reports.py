from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from modules.reports_billing import BillingReport
from modules.reports_inventory import InventoryReport
from modules.reports_appointments import AppointmentsReport

class ReportsModule(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        tabs = QTabWidget()

        tabs.addTab(BillingReport(embed=True), "Billing Report")
        tabs.addTab(InventoryReport(embed=True), "Inventory Report")
        tabs.addTab(AppointmentsReport(embed=True), "Appointments Report")

        layout.addWidget(tabs)
        self.setLayout(layout)
    # def showEvent(self, event):
    #     super().showEvent(event)
    #     self.load_patients()  # Reload patients every time tab is shown