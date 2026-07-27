import io
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_invoice_pdf(order):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1))
    
    # Header
    elements.append(Paragraph("<b>Birdwing E-Store</b>", styles['Title']))
    elements.append(Paragraph("123 Commerce St, Tech City, IN 110001", styles['Center']))
    elements.append(Paragraph("Email: support@birdwing.com | Phone: +91 9999999999", styles['Center']))
    elements.append(Spacer(1, 24))
    
    # Billing Info
    elements.append(Paragraph(f"<b>Invoice To:</b> {order.name}", styles['Normal']))
    elements.append(Paragraph(f"<b>Email:</b> {order.email}", styles['Normal']))
    elements.append(Paragraph(f"<b>Phone:</b> {order.phone}", styles['Normal']))
    elements.append(Paragraph(f"<b>Address:</b> {order.address1} {order.address2}, {order.city}, {order.state} - {order.zip_code}", styles['Normal']))
    elements.append(Spacer(1, 24))
    
    # Order Details
    elements.append(Paragraph(f"<b>Order ID:</b> {order.order_id}", styles['Normal']))
    elements.append(Paragraph(f"<b>Payment Status:</b> {order.payment_status}", styles['Normal']))
    if order.razorpay_payment_id:
        elements.append(Paragraph(f"<b>Payment Reference:</b> {order.razorpay_payment_id}", styles['Normal']))
    elements.append(Spacer(1, 24))
    
    # Items Table
    data = [['Product Name', 'Quantity', 'Unit Price (INR)', 'Total (INR)']]
    
    try:
        cart = json.loads(order.items_json)
        total_price = 0
        for item in cart.values():
            qty = item[0]
            name = item[1]
            price = item[2]
            item_total = qty * price
            total_price += item_total
            data.append([name, str(qty), str(price), str(item_total)])
            
        data.append(['', '', 'Grand Total', str(total_price)])
    except Exception:
        data.append(['Error loading items', '', '', ''])
    
    t = Table(data, colWidths=[200, 80, 100, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(t)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
