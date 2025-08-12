import base64

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QFormLayout, QMessageBox, QHBoxLayout, QSpinBox
)
from PyQt5.QtCore import Qt
import sqlite3
import os
import re
import webbrowser
from datetime import datetime
from database.db_config import DB_PATH
import html


def save_billing_record(patient_id, patient_display, doctor, total_amount):
    pass


class BillingModule(QWidget):
    """
    BillingModule with:
    - Multi-item billing (description, qty, rate, item discount, item extra charge)
    - Live totals
    - Save bill summary to DB (keeps compatibility)
    - Export invoice as HTML (printer-friendly), opens automatically
    """

    def __init__(self):
        super().__init__()
        self.logo_path = os.path.join(os.getcwd(), "Support", "watermark.png")
        self.clinic_name = "Dr. N's Dental Studio"
        self.clinic_address_lines = [
            "First Floor, Chovattukunnel Plaza",
            "Erattupetta Road, Edappady, Pala",
            "Bharananganam, Kerala 686578"
        ]
        self.clinic_contact = "Phone: +91-XXXXXXXXXX"

        self.init_ui()
        self.init_db()
        self.load_patients()
        self.load_doctors()
        self.load_bills()
    def showEvent(self, event):
        super().showEvent(event)
        self.load_patients()
        self.load_doctors()
        self.load_bills()  # Reload patients every time tab is shown

    def init_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        # Patient & doctor selectors
        self.patient_combo = QComboBox()
        form_layout.addRow("Patient:", self.patient_combo)

        self.doctor_combo = QComboBox()
        form_layout.addRow("Doctor:", self.doctor_combo)

        # Item inputs: description, qty, rate, discount, extra
        item_row = QHBoxLayout()
        self.item_desc = QLineEdit()
        self.item_desc.setPlaceholderText("Description")
        item_row.addWidget(self.item_desc)

        self.item_qty = QSpinBox()
        self.item_qty.setRange(1, 1000)
        self.item_qty.setValue(1)
        item_row.addWidget(self.item_qty)

        self.item_rate = QLineEdit()
        self.item_rate.setPlaceholderText("Rate")
        item_row.addWidget(self.item_rate)

        self.item_discount = QLineEdit()
        self.item_discount.setPlaceholderText("Discount")
        item_row.addWidget(self.item_discount)

        self.item_extra = QLineEdit()
        self.item_extra.setPlaceholderText("Extra")
        item_row.addWidget(self.item_extra)

        self.add_item_btn = QPushButton("Add Item")
        self.add_item_btn.clicked.connect(self.add_item)
        item_row.addWidget(self.add_item_btn)

        form_layout.addRow(QLabel("Add Item (Desc | Qty | Rate | Discount | Extra)"), item_row)

        # Buttons: remove selected item, clear items
        btn_row = QHBoxLayout()
        self.remove_item_btn = QPushButton("Remove Selected Item")
        self.remove_item_btn.clicked.connect(self.remove_selected_item)
        btn_row.addWidget(self.remove_item_btn)

        self.clear_items_btn = QPushButton("Clear Items")
        self.clear_items_btn.clicked.connect(self.clear_items)
        btn_row.addWidget(self.clear_items_btn)

        form_layout.addRow(btn_row)

        # Invoice-level notes / discounts / extra charges
        self.invoice_discount = QLineEdit()
        self.invoice_discount.setPlaceholderText("Invoice-wide discount (₹)")
        form_layout.addRow("Invoice Discount (₹):", self.invoice_discount)

        self.invoice_extra = QLineEdit()
        self.invoice_extra.setPlaceholderText("Invoice-wide extra charges (₹)")
        form_layout.addRow("Invoice Extra (₹):", self.invoice_extra)

        # Generate button
        self.generate_btn = QPushButton("Save & Generate Invoice (HTML)")
        self.generate_btn.clicked.connect(self.generate_bill)
        form_layout.addWidget(self.generate_btn)

        layout.addLayout(form_layout)

        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels(["Description", "Qty", "Rate (₹)", "Discount (₹)", "Extra (₹)", "Line Total (₹)"])
        layout.addWidget(QLabel("Invoice Items:"))
        layout.addWidget(self.items_table)

        # Summary labels
        self.total_label = QLabel("Total: ₹ 0.00")
        layout.addWidget(self.total_label)

        # Generated bills table (history)
        self.bills_table = QTableWidget()
        self.bills_table.setColumnCount(5)
        self.bills_table.setHorizontalHeaderLabels(["Bill ID", "Patient", "Doctor", "Total (₹)", "Date"])
        layout.addWidget(QLabel("Generated Bills:"))
        layout.addWidget(self.bills_table)

        self.setLayout(layout)

        # Connect changes to recalc totals
        self.invoice_discount.textChanged.connect(self.recalculate_totals)
        self.invoice_extra.textChanged.connect(self.recalculate_totals)

    # ----------------- DB -----------------
    def init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                patient_name TEXT,
                doctor TEXT,
                total_amount REAL,
                bill_date TEXT
            )
        """)
        conn.commit()
        conn.close()

    def load_patients(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT patient_id, name FROM patients")
            patients = cursor.fetchall()
        except Exception:
            patients = []
        self.patient_combo.clear()
        for pid, name in patients:
            self.patient_combo.addItem(f"{name} (ID:{pid})", pid)
        conn.close()

    def load_doctors(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT DISTINCT doctor FROM appointments WHERE doctor IS NOT NULL")
            doctors = [row[0] for row in cursor.fetchall() if row[0]]
            self.doctor_combo.clear()
            self.doctor_combo.addItems(doctors)
        except Exception:
            self.doctor_combo.clear()
        finally:
            conn.close()

    def load_bills(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT bill_id, patient_name, doctor, total_amount, bill_date FROM bills ORDER BY bill_id DESC")
            bills = cursor.fetchall()
        except Exception:
            bills = []
        conn.close()

        self.bills_table.setRowCount(0)
        for r, row in enumerate(bills):
            self.bills_table.insertRow(r)
            for c, val in enumerate(row):
                self.bills_table.setItem(r, c, QTableWidgetItem(str(val)))

    # ----------------- Items handling -----------------
    def add_item(self):
        desc = self.item_desc.text().strip()
        qty = int(self.item_qty.value())
        rate_text = self.item_rate.text().strip()
        disc_text = self.item_discount.text().strip() or "0"
        extra_text = self.item_extra.text().strip() or "0"

        if not desc:
            QMessageBox.warning(self, "Input Error", "Please enter an item description.")
            return

        try:
            rate = float(rate_text)
            discount = float(disc_text)
            extra = float(extra_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Rate, discount and extra must be numbers.")
            return

        line_total = qty * rate - discount + extra
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        self.items_table.setItem(row, 0, QTableWidgetItem(desc))
        self.items_table.setItem(row, 1, QTableWidgetItem(str(qty)))
        self.items_table.setItem(row, 2, QTableWidgetItem(f"{rate:.2f}"))
        self.items_table.setItem(row, 3, QTableWidgetItem(f"{discount:.2f}"))
        self.items_table.setItem(row, 4, QTableWidgetItem(f"{extra:.2f}"))
        self.items_table.setItem(row, 5, QTableWidgetItem(f"{line_total:.2f}"))

        # Clear small inputs (keep patient/doctor)
        self.item_desc.clear()
        self.item_rate.clear()
        self.item_discount.clear()
        self.item_extra.clear()
        self.item_qty.setValue(1)

        self.recalculate_totals()

    def remove_selected_item(self):
        r = self.items_table.currentRow()
        if r >= 0:
            self.items_table.removeRow(r)
            self.recalculate_totals()
        else:
            QMessageBox.information(self, "Remove Item", "Select an item row to remove.")

    def clear_items(self):
        self.items_table.setRowCount(0)
        self.recalculate_totals()

    def recalculate_totals(self):
        total = 0.0
        for r in range(self.items_table.rowCount()):
            try:
                amt_item = float(self.items_table.item(r, 5).text())
            except Exception:
                amt_item = 0.0
            total += amt_item

        try:
            inv_disc = float(self.invoice_discount.text()) if self.invoice_discount.text().strip() else 0.0
        except ValueError:
            inv_disc = 0.0
        try:
            inv_extra = float(self.invoice_extra.text()) if self.invoice_extra.text().strip() else 0.0
        except ValueError:
            inv_extra = 0.0

        total_final = total - inv_disc + inv_extra
        self.total_label.setText(f"Total: ₹ {total_final:.2f}")
        return total_final
    

    # ----------------- Invoice generation -----------------
    def generate_bill(self):
        patient_display = self.patient_combo.currentText()
        patient_id = self.patient_combo.currentData()
        doctor = self.doctor_combo.currentText()

        if not patient_display or patient_display.strip() == "":
            QMessageBox.warning(self, "Input Error", "Please select a patient.")
            return
        if self.items_table.rowCount() == 0:
            QMessageBox.warning(self, "Input Error", "Please add at least one item to the invoice.")
            return

        # Gather items
        items = []
        for r in range(self.items_table.rowCount()):
            desc = self.items_table.item(r, 0).text()
            qty = float(self.items_table.item(r, 1).text())
            rate = float(self.items_table.item(r, 2).text())
            disc = float(self.items_table.item(r, 3).text())
            extra = float(self.items_table.item(r, 4).text())
            line_total = float(self.items_table.item(r, 5).text())
            items.append({
                "description": desc,
                "qty": qty,
                "rate": rate,
                "discount": disc,
                "extra": extra,
                "line_total": line_total
            })

        invoice_discount = float(self.invoice_discount.text()) if self.invoice_discount.text().strip() else 0.0
        invoice_extra = float(self.invoice_extra.text()) if self.invoice_extra.text().strip() else 0.0

        total_amount = sum(i["line_total"] for i in items) - invoice_discount + invoice_extra
        total_amount = round(total_amount, 2)

        # Save summary to DB
        bill_date = datetime.now().strftime("%Y-%m-%d")
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # cursor.execute("""
            #     INSERT INTO bills (patient_id, patient_name, doctor, amount, bill_date)
            #     VALUES (?, ?, ?, ?, ?)
            # """, (patient_id, patient_display, doctor, total_amount, bill_date))
            cursor.execute("""
                INSERT INTO bills (patient_id, patient_name, doctor, treatment, amount, bill_date)
                VALUES (?, ?, ?, ?, ?, DATE('now'))
            """, (patient_id, patient_display, doctor, total_amount, bill_date))

            conn.commit()
            bill_id = cursor.lastrowid
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save bill: {e}")
            return

        # Generate HTML invoice file
        try:
            
            filepath = self.generate_invoice_html(
                bill_id=bill_id,
                patient_display=patient_display,
                patient_id=patient_id,
                doctor=doctor,
                items=items,
                invoice_discount=invoice_discount,
                invoice_extra=invoice_extra,
                total_amount=total_amount,
                bill_date=bill_date
            )
            

            # reload bills list
            self.load_bills()
            QMessageBox.information(self, "Success", f"Invoice generated: {filepath}")
            # open in default browser
            webbrowser.open(f"file://{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate invoice: {e}")

    def sanitize_filename(self, s):
        # remove unsafe characters
        return re.sub(r'[<>:"/\\|?*]', '_', s)
    
    
    def generate_invoice_html(self, bill_id, patient_display, patient_id, doctor,
                              items, invoice_discount, invoice_extra, total_amount, bill_date):
        # Build filename
        name_only = re.sub(r"\s*\(ID:\d+\)\s*$", "", patient_display).strip()
        safe_name = self.sanitize_filename(name_only.replace(" ", "_"))
        date_str = datetime.now().strftime("%Y%m%d")
        file_name = f"INVOICE_{safe_name}_ID{patient_id}_{date_str}.html"
        file_path = os.path.join(os.getcwd(), "Invoice", file_name)

        # Get watermark logo path
        if os.path.exists(self.logo_path):
            logo_path_local = self.logo_path.replace("\\", "/")
        else:
            logo_path_local = ""

        clinic_address_html = "<br>".join(html.escape(l) for l in self.clinic_address_lines)
        save_billing_record(patient_id, patient_display, doctor, total_amount)
        # Items rows
        items_rows_html = ""
        for it in items:
            qty_display = int(it['qty']) if it['qty'].is_integer() else it['qty']
            items_rows_html += f"""
            <tr>
                <td>{html.escape(it['description'])}</td>
                <td style="text-align:center;">{qty_display}</td>
                <td style="text-align:right;">{it['rate']:.2f}</td>
                <td style="text-align:right;">{it['discount']:.2f}</td>
                <td style="text-align:right;">{it['extra']:.2f}</td>
                <td style="text-align:right;">{it['line_total']:.2f}</td>
            </tr>
            """

        html_content = f"""<!doctype html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>Invoice {bill_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            color:#222;
            margin:30px;
            position: relative;
        }}
        body::before {{
            content: "";
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: url('file://{logo_path_local}') no-repeat center;
            background-size: 60%;
            opacity: 0.08;
            z-index: -1;
            width: 100%;
            height: 100%;
        }}
        .header {{ display:flex; justify-content:space-between; align-items:center; }}
        .clinic-info {{ text-align:left; }}
        .clinic-name {{ font-size:20px; font-weight:700; }}
        .invoice-meta {{ text-align:right; }}
        .invoice-title {{ font-size:28px; color:#666; letter-spacing:2px; }}
        hr {{ border:none; border-top:1px solid #eee; margin:12px 0 18px 0; }}
        table {{ width:100%; border-collapse:collapse; margin-top:10px; }}
        th, td {{ padding:8px 10px; border:1px solid #ddd; font-size:14px; }}
        th {{ background:#f5f8fb; text-align:left; }}
        .right {{ text-align:right; }}
        .summary-table td {{ border:none; padding:6px; }}
        .notes-box {{ border:1px dashed #ccc; padding:10px; margin-top:14px; min-height:40px; }}
        .payment-box {{ border:1px solid #ddd; padding:10px; margin-top:12px; }}
        .total-row td {{ font-weight:700; font-size:16px; }}
        .small {{ font-size:12px; color:#666; }}
        @media print {{
            .no-print {{ display:none; }}
        }}
    </style>
    </head>
    <body>
    <div class="header">
        <div class="clinic-info">
            <div class="clinic-name">{html.escape(self.clinic_name)}</div>
            <div class="small">{clinic_address_html}</div>
            <div class="small">{html.escape(self.clinic_contact)}</div>
        </div>
        <div class="invoice-meta">
            <div class="invoice-title">INVOICE</div>
            <div><strong>Date:</strong> {html.escape(bill_date)}</div>
            <div><strong>Invoice #:</strong> {bill_id}</div>
        </div>
    </div>
    <hr>

    <div style="display:flex; justify-content:space-between;">
        <div>
            <strong>Bill To:</strong><br>
            {html.escape(patient_display)}
        </div>
        <div>
            <strong>Patient ID:</strong> {html.escape(str(patient_id))}<br>
            <strong>Doctor:</strong> {html.escape(doctor)}
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th style="width:45%;">Description</th>
                <th style="width:8%; text-align:center;">Qty</th>
                <th style="width:12%; text-align:right;">Rate (₹)</th>
                <th style="width:10%; text-align:right;">Discount (₹)</th>
                <th style="width:10%; text-align:right;">Extra (₹)</th>
                <th style="width:15%; text-align:right;">Line Total (₹)</th>
            </tr>
        </thead>
        <tbody>
            {items_rows_html}
        </tbody>
    </table>

    <table class="summary-table" style="width:100%; margin-top:10px;">
        <tr>
            <td style="width:70%;"></td>
            <td style="width:30%;">
                <table style="width:100%;">
                    <tr><td>Subtotal:</td><td style="text-align:right;">₹ {sum(it['line_total'] for it in items):.2f}</td></tr>
                    <tr><td>Invoice Discount:</td><td style="text-align:right;">₹ {invoice_discount:.2f}</td></tr>
                    <tr><td>Extra Charges:</td><td style="text-align:right;">₹ {invoice_extra:.2f}</td></tr>
                    <tr class="total-row"><td>TOTAL:</td><td style="text-align:right;">₹ {total_amount:.2f}</td></tr>
                </table>
            </td>
        </tr>
    </table>

    <div class="payment-box">
        <strong>Payment Type:</strong> ______________________ &nbsp;&nbsp;
        <strong>Cardholder Name:</strong> ______________________
        <div style="margin-top:8px;" class="small">If paying by card, please fill card details on the printed copy if needed.</div>
    </div>

    <div class="notes-box">
        <strong>Notes:</strong><br>
    </div>

    <div style="margin-top:18px; text-align:center;">
        <small class="small">Thank you for choosing {html.escape(self.clinic_name)}!</small>
    </div>

    </body>
    </html>
    """
        # Save HTML file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return file_path

