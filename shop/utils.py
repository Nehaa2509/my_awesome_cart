import io
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_invoice_pdf(order):
    """
    Generates an editorial, high-end PDF invoice for an Order instance,
    matching the OQIREL frontend color scheme (#6b443a, #fdf6f9, #edd7c2, #f09fc1, #98f0e3).
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
    
    # 🎨 Brand Palette Tokens matching frontend design system
    color_brown = colors.HexColor('#6b443a')
    color_bg = colors.HexColor('#fdf6f9')
    color_nude = colors.HexColor('#edd7c2')
    color_pink = colors.HexColor('#f09fc1')
    color_mint = colors.HexColor('#98f0e3')
    color_dark = colors.HexColor('#3a241e')

    # Custom Editorial Typography Styles
    brand_style = ParagraphStyle(
        'BrandHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=color_brown
    )
    
    tagline_style = ParagraphStyle(
        'BrandTagline',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=color_pink
    )

    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=2, # Right aligned
        textColor=color_brown
    )
    
    meta_style = ParagraphStyle(
        'InvoiceMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        alignment=2, # Right aligned
        textColor=color_dark
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=color_brown,
        spaceAfter=6
    )
    
    normal_style = ParagraphStyle(
        'InvoiceNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=color_dark
    )

    header_table_cell_style = ParagraphStyle(
        'HeaderTableCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.white
    )

    story = []

    # 1. Header Section (Brand Name & Invoice Title)
    header_data = [
        [
            Paragraph("OQIREL", brand_style),
            Paragraph("TAX INVOICE", title_style)
        ],
        [
            Paragraph("THOUGHTFULLY CURATED &bull; MADE FOR YOU", tagline_style),
            Paragraph(f"<b>Invoice #:</b> INV-{order.order_id}<br/><b>Status:</b> {order.payment_status}", meta_style)
        ]
    ]
    
    header_table = Table(header_data, colWidths=[300, 240])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))

    # Divider bar with Pink Accent
    divider = Table([['']], colWidths=[540], rowHeights=[3])
    divider.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), color_pink)]))
    story.append(divider)
    story.append(Spacer(1, 15))

    # 2. Billing & Shipping Customer Matrix
    address_str = f"{order.address1}"
    if order.address2:
        address_str += f", {order.address2}"
    address_str += f", {order.city}, {order.state} - {order.zip_code}"

    customer_info = f"""
    <b>Billed To:</b> {order.name}<br/>
    <b>Email:</b> {order.email}<br/>
    <b>Phone:</b> {order.phone}<br/>
    <b>Shipping Destination:</b> {address_str}
    """
    
    order_meta = f"""
    <b>Order ID:</b> #{order.order_id}<br/>
    <b>Payment Gateway:</b> Razorpay Online<br/>
    <b>Payment Status:</b> <font color="#2b7a78"><b>{order.payment_status}</b></font><br/>
    <b>Razorpay Order ID:</b> {order.razorpay_order_id or 'N/A'}
    """

    billing_data = [
        [Paragraph("CUSTOMER DETAILS", section_heading), Paragraph("ORDER SUMMARY", section_heading)],
        [Paragraph(customer_info, normal_style), Paragraph(order_meta, normal_style)]
    ]
    
    billing_table = Table(billing_data, colWidths=[270, 270])
    billing_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (-1,-1), color_bg),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 1, color_nude),
    ]))
    story.append(billing_table)
    story.append(Spacer(1, 18))

    # 3. Itemized Products Table
    story.append(Paragraph("ITEMIZED PURCHASES", section_heading))
    story.append(Spacer(1, 6))

    table_data = [
        [
            Paragraph("<b>#</b>", header_table_cell_style),
            Paragraph("<b>Item Description</b>", header_table_cell_style),
            Paragraph("<b>Qty</b>", header_table_cell_style),
            Paragraph("<b>Unit Price</b>", header_table_cell_style),
            Paragraph("<b>Total Amount</b>", header_table_cell_style)
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
        grand_total = order.amount
        table_data.append([
            Paragraph("1", normal_style),
            Paragraph("Order Items Package", normal_style),
            Paragraph("1", normal_style),
            Paragraph(f"INR {order.amount:,.2f}", normal_style),
            Paragraph(f"INR {order.amount:,.2f}", normal_style)
        ])

    # Grand Total Row
    total_title_style = ParagraphStyle('TotalTitle', parent=normal_style, fontName='Helvetica-Bold', textColor=color_brown)
    total_val_style = ParagraphStyle('TotalVal', parent=normal_style, fontName='Helvetica-Bold', textColor=color_brown)

    table_data.append([
        Paragraph("", normal_style),
        Paragraph("<b>GRAND TOTAL</b>", total_title_style),
        Paragraph("", normal_style),
        Paragraph("", normal_style),
        Paragraph(f"<b>INR {grand_total:,.2f}</b>", total_val_style)
    ])

    items_table = Table(table_data, colWidths=[30, 250, 50, 105, 105])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), color_brown),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-2), 0.5, color_nude),
        # Grand Total Row styling with nude background & pink accent line
        ('BACKGROUND', (0,-1), (-1,-1), color_nude),
        ('LINEABOVE', (0,-1), (-1,-1), 2, color_pink),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
    ]))

    story.append(items_table)
    story.append(Spacer(1, 25))

    # 4. Footer & Support Info Strip
    footer_text = ParagraphStyle(
        'FooterText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        alignment=1, # Center
        textColor=color_brown
    )
    story.append(Paragraph("Thank you for shopping with <b>OQIREL</b>! Built with care, Razorpay, and Django.", footer_text))

    doc.build(story)
    buffer.seek(0)
    return buffer
