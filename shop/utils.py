import io
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_invoice_pdf(order):
    """
    Generates a professional PDF invoice for a given Order model instance.
    Returns a BytesIO buffer containing the PDF binary data.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    brand_style = ParagraphStyle(
        'BrandHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0d6efd')
    )
    
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=2, # Right aligned
        textColor=colors.HexColor('#212529')
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#495057'),
        spaceAfter=6
    )
    
    normal_style = ParagraphStyle(
        'InvoiceNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#212529')
    )

    story = []

    # 1. Header Section (Brand Name & Invoice Details)
    header_data = [
        [
            Paragraph("Birdwing E-Store", brand_style),
            Paragraph("INVOICE", title_style)
        ],
        [
            Paragraph("Official Purchase Receipt & Tax Invoice", normal_style),
            Paragraph(f"<b>Invoice #:</b> INV-{order.order_id}<br/><b>Date:</b> {order.payment_status}", normal_style)
        ]
    ]
    
    header_table = Table(header_data, colWidths=[300, 240])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))

    # Divider line
    divider = Table([['']], colWidths=[540], rowHeights=[2])
    divider.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e9ecef'))]))
    story.append(divider)
    story.append(Spacer(1, 15))

    # 2. Billing Information Section
    address_str = f"{order.address1}"
    if order.address2:
        address_str += f", {order.address2}"
    address_str += f", {order.city}, {order.state} - {order.zip_code}"

    customer_info = f"""
    <b>Billed To:</b> {order.name}<br/>
    <b>Email:</b> {order.email}<br/>
    <b>Phone:</b> {order.phone}<br/>
    <b>Shipping Address:</b> {address_str}
    """
    
    order_meta = f"""
    <b>Order ID:</b> #{order.order_id}<br/>
    <b>Payment Method:</b> Razorpay Online<br/>
    <b>Payment Status:</b> <font color="green"><b>{order.payment_status}</b></font><br/>
    <b>Razorpay Order ID:</b> {order.razorpay_order_id or 'N/A'}
    """

    billing_data = [
        [Paragraph("CUSTOMER DETAILS", section_heading), Paragraph("ORDER SUMMARY", section_heading)],
        [Paragraph(customer_info, normal_style), Paragraph(order_meta, normal_style)]
    ]
    
    billing_table = Table(billing_data, colWidths=[270, 270])
    billing_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
    ]))
    story.append(billing_table)
    story.append(Spacer(1, 20))

    # 3. Itemized Products Table
    story.append(Paragraph("ITEMIZED PURCHASES", section_heading))
    story.append(Spacer(1, 6))

    table_data = [
        [
            Paragraph("<b>#</b>", normal_style),
            Paragraph("<b>Item Description</b>", normal_style),
            Paragraph("<b>Qty</b>", normal_style),
            Paragraph("<b>Unit Price</b>", normal_style),
            Paragraph("<b>Total Amount</b>", normal_style)
        ]
    ]

    grand_total = 0
    item_counter = 1

    try:
        cart = json.loads(order.items_json) if isinstance(order.items_json, str) else order.items_json
        for key, item in cart.items():
            qty = item[0]
            name = item[1]
            price = item[2]
            line_total = qty * price
            grand_total += line_total

            table_data.append([
                Paragraph(str(item_counter), normal_style),
                Paragraph(name, normal_style),
                Paragraph(str(qty), normal_style),
                Paragraph(f"INR {price:,.2f}", normal_style),
                Paragraph(f"INR {line_total:,.2f}", normal_style)
            ])
            item_counter += 1
    except Exception:
        # Fallback if json parsing fails
        grand_total = order.amount
        table_data.append([
            Paragraph("1", normal_style),
            Paragraph("Order Items Package", normal_style),
            Paragraph("1", normal_style),
            Paragraph(f"INR {order.amount:,.2f}", normal_style),
            Paragraph(f"INR {order.amount:,.2f}", normal_style)
        ])

    # Grand Total Row
    table_data.append([
        Paragraph("", normal_style),
        Paragraph("<b>GRAND TOTAL</b>", normal_style),
        Paragraph("", normal_style),
        Paragraph("", normal_style),
        Paragraph(f"<b>INR {grand_total:,.2f}</b>", normal_style)
    ])

    items_table = Table(table_data, colWidths=[30, 250, 50, 105, 105])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#dee2e6')),
        # Styling for Grand Total row
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e9ecef')),
        ('LINEABOVE', (0,-1), (-1,-1), 1.5, colors.HexColor('#0d6efd')),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
    ]))
    
    # Fix header row text color in reportlab table
    for i in range(5):
        table_data[0][i].style.textColor = colors.white

    story.append(items_table)
    story.append(Spacer(1, 30))

    # 4. Footer Thank You Note
    footer_text = ParagraphStyle(
        'FooterText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        alignment=1, # Center
        textColor=colors.HexColor('#6c757d')
    )
    story.append(Paragraph("Thank you for shopping with Birdwing E-Store! If you have any questions, contact support.", footer_text))

    doc.build(story)
    buffer.seek(0)
    return buffer
