from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import os

CLINIC_NAME = "Dr. N's Dental Studio"
CLINIC_ADDRESS = "First Floor, Chovattukunnel Plaza, Erattupetta Road,\nEdappady, Pala, Bharananganam, Kerala 686578"
DOCTOR_NAME = "Dr. Neethu Mathew"
LOGO_PATH = "DrWs_Dental_Studio_Icon.ico"  # Ensure path is correct

def add_header_footer(canvas_obj, doc):
    width, height = A4
    # Logo
    if os.path.exists(LOGO_PATH):
        canvas_obj.drawImage(LOGO_PATH, 1.5*cm, height - 3*cm, width=2*cm, height=2*cm, preserveAspectRatio=True)

    # Clinic Info
    styles = getSampleStyleSheet()
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
    canvas_obj.setFont("HeiseiMin-W3", 12)
    text = f"{CLINIC_NAME}\n{CLINIC_ADDRESS}\nDoctor: {DOCTOR_NAME}"
    for i, line in enumerate(text.split("\n")):
        canvas_obj.drawString(4*cm, height - (1.5 + i*0.5)*cm, line)

def export_pdf(file_path, title, data, col_widths=None):
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"<b>{title}</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    # Table
    if data:
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No data available.", styles['Normal']))

    def on_first_page(canvas_obj, doc):
        add_header_footer(canvas_obj, doc)

    def on_later_pages(canvas_obj, doc):
        add_header_footer(canvas_obj, doc)

    doc.build(elements, onFirstPage=on_first_page, onLaterPages=on_later_pages)
