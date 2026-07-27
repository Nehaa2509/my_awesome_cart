import io
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def generate_invoice_pdf(order):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=72, 
        leftMargin=72, 
        topMargin=72, 
        bottomMargin=18
    )
    elements = []
    styles = getSampleStyleSheet()
    
    # Document Header & Meta Data Profiles
    elements.append(Paragraph("<b>Birdwing E-Store</b>", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Invoice Reference ID:</b> BWD-{order.order_id:06d}", styles['Normal']))
    elements.append(Paragraph(f"<b>Invoice To:</b> {order.name} ({order.email})", styles['Normal']))
    elements.append(Spacer(1, 18))
    
    # Grid Data Processing Setup
    table_headers = ['Product Name', 'Quantity', 'Unit Price (INR)', 'Total (INR)']
    data = [table_headers]
    
    # Leverage reverse relational prefetch properties from structural design migrations
    order_items = order.items.select_related('product').all()
    calculated_grand_total = 0
    
    if order_items.exists():
        for item in order_items:
            qty = item.quantity
            name = item.product.product_name
            historical_price = item.price_at_purchase
            row_total = qty * historical_price
            calculated_grand_total += row_total
            
            data.append([name, str(qty), f"{historical_price}.00", f"{row_total}.00"])
    elif order.items_json:
        # Fallback for legacy order JSON snapshots
        try:
            cart = json.loads(order.items_json)
            for item in cart.values():
                qty = item[0] if isinstance(item, list) else item
                name = item[1] if isinstance(item, list) and len(item) > 1 else "Product"
                price = item[2] if isinstance(item, list) and len(item) > 2 else 0
                row_total = qty * price
                calculated_grand_total += row_total
                data.append([name, str(qty), f"{price}.00", f"{row_total}.00"])
        except Exception:
            data.append(['Error loading items', '', '', ''])
        
    # Inject Final Summary Layout Footers
    data.append(['', '', 'Grand Total', f"{calculated_grand_total}.00"])
    
    # Render Structural Content Grids
    invoice_table = Table(data, colWidths=[220, 60, 100, 80])
    invoice_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#232F3E')),  # Amazon-inspired slate signature background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.lightgrey),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#232F3E')),
        ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(invoice_table)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
