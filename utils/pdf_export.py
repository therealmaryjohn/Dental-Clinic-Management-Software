import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

CLINIC_NAME = "Dr. N's Dental Studio"
CLINIC_ADDRESS = "First Floor, Chovattukunnel Plaza, Erattupetta Road, Edappady, Pala, Bharananganam, Kerala 686578"
DOCTOR_NAME = "Dr. Neethu Mathew"
LOGO_PATH = os.path.join("assets", "DrWs_Dental_Studio_Icon.ico")  # change if needed


def export_report_to_pdf(title, table_headers, table_data, filename):
    pdf_path = os.path.join("reports", filename)
    os.makedirs("reports", exist_ok=True)

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name="TitleStyle", parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=10)
    header_style = ParagraphStyle(name="HeaderStyle", parent=styles['Normal'], alignment=1, fontSize=10)

    # --- Logo and Clinic Info ---
    if os.path.exists(LOGO_PATH):
        logo = Image(LOGO_PATH, width=50, height=50)
        elements.append(logo)
    elements.append(Paragraph(f"<b>{CLINIC_NAME}</b>", styles['Title']))
    elements.append(Paragraph(CLINIC_ADDRESS, styles['Normal']))
    elements.append(Paragraph(f"<b>Doctor:</b> {DOCTOR_NAME}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # --- Report Title ---
    elements.append(Paragraph(f"<b>{title}</b>", title_style))
    elements.append(Spacer(1, 12))

    # --- Table Data ---
    data = [table_headers] + table_data
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))
    elements.append(table)

    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)
    return pdf_path


def add_watermark(canvas_obj, doc):
    """Adds watermark to each page"""
    if os.path.exists(LOGO_PATH):
        canvas_obj.saveState()
        canvas_obj.setFillAlpha(0.1)
        canvas_obj.drawImage(LOGO_PATH, A4[0] / 4, A4[1] / 3, width=300, height=300, mask='auto')
        canvas_obj.restoreState()
