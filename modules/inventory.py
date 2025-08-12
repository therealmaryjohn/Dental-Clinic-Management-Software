from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QHBoxLayout
)
import sqlite3
import os
from database.db_config import DB_PATH


class InventoryModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management")

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.item_name_input = QLineEdit()
        self.quantity_input = QLineEdit()

        form_layout.addRow("Item Name:", self.item_name_input)
        form_layout.addRow("Quantity:", self.quantity_input)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Item")
        self.stock_out_button = QPushButton("Stock Out")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.stock_out_button)

        self.add_button.clicked.connect(self.add_item)
        self.stock_out_button.clicked.connect(self.stock_out_item)

        layout.addLayout(form_layout)
        layout.addLayout(button_layout)

        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(2)
        self.inventory_table.setHorizontalHeaderLabels(["Item", "Quantity"])
        layout.addWidget(QLabel("Inventory List:"))
        layout.addWidget(self.inventory_table)

        self.setLayout(layout)
        self.init_db()
        self.load_inventory()

    def init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                item_name TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def load_inventory(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, quantity FROM inventory")
        records = cursor.fetchall()
        conn.close()

        self.inventory_table.setRowCount(0)
        for row_idx, (item, qty) in enumerate(records):
            self.inventory_table.insertRow(row_idx)
            self.inventory_table.setItem(row_idx, 0, QTableWidgetItem(item))
            self.inventory_table.setItem(row_idx, 1, QTableWidgetItem(str(qty)))
        self.check_low_stock()

    def add_item(self):
        item_name = self.item_name_input.text().strip()
        try:
            quantity = int(self.quantity_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Quantity must be a number.")
            return

        if not item_name or quantity <= 0:
            QMessageBox.warning(self, "Input Error", "Please enter valid item name and quantity.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT quantity FROM inventory WHERE item_name = ?", (item_name,))
        existing = cursor.fetchone()
        if existing:
            new_qty = existing[0] + quantity
            cursor.execute("UPDATE inventory SET quantity = ? WHERE item_name = ?", (new_qty, item_name))
        else:
            cursor.execute("INSERT INTO inventory (item_name, quantity) VALUES (?, ?)", (item_name, quantity))
        conn.commit()
        conn.close()

        self.item_name_input.clear()
        self.quantity_input.clear()
        self.load_inventory()
        self.check_low_stock()

    def stock_out_item(self):
        item_name = self.item_name_input.text().strip()
        try:
            quantity = int(self.quantity_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Quantity must be a number.")
            return

        if not item_name or quantity <= 0:
            QMessageBox.warning(self, "Input Error", "Please enter valid item name and quantity.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT quantity FROM inventory WHERE item_name = ?", (item_name,))
        existing = cursor.fetchone()
        if not existing:
            QMessageBox.warning(self, "Not Found", "Item not found in inventory.")
            conn.close()
            return

        current_qty = existing[0]
        if quantity > current_qty:
            QMessageBox.warning(self, "Insufficient Stock", f"Only {current_qty} units available.")
            conn.close()
            return

        new_qty = current_qty - quantity
        cursor.execute("UPDATE inventory SET quantity = ? WHERE item_name = ?", (new_qty, item_name))
        conn.commit()
        conn.close()

        self.item_name_input.clear()
        self.quantity_input.clear()
        self.load_inventory()
        self.check_low_stock()

    def check_low_stock(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        threshold = 5  # Set your threshold here
        cursor.execute("SELECT item_name, quantity FROM inventory WHERE quantity < ?", (threshold,))
        low_stock_items = cursor.fetchall()
        conn.close()

        if low_stock_items:
            alert_message = "Low stock warning for the following items:\n"
            for item, qty in low_stock_items:
                alert_message += f"- {item}: {qty} left\n"
            QMessageBox.warning(self, "Low Stock Alert", alert_message)
