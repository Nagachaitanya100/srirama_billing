from reportlab.lib.pagesizes import A5
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from .template_manager import TemplateManager
import os
import logging

logger = logging.getLogger(__name__)

# Create styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name='RightAlign',
    parent=styles['Normal'],
    alignment=TA_RIGHT
))
styles.add(ParagraphStyle(
    name='CenterAlign',
    parent=styles['Normal'],
    alignment=TA_CENTER
))

def add_refined_border(canvas, doc):
    """
    Add refined 1pt border around all sides of A5 page (20pt spacing)
    """
    page_width, page_height = A5
    border_margin = 20

    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1)
    canvas.rect(
        border_margin,
        border_margin,  
        page_width - 2 * border_margin,
        page_height - 2 * border_margin
    )

def calculate_items_subtotal(items):
    """Calculate subtotal from items"""
    return sum(getattr(item, 'quantity', 1) * getattr(item, 'unit_price', 0.0) for item in items)

def extract_item_data_safely(item, logger):
    """Extract item data with multiple fallback strategies"""
    try:
        item_name = 'Item'
        item_description = ''

        # Strategy 1: Try nested item.item.name and item.item.description
        if hasattr(item, 'item') and item.item:
            if hasattr(item.item, 'name'):
                item_name = str(item.item.name)

            if hasattr(item.item, 'description'):
                item_description = str(item.item.description) if item.item.description else ''

        # Strategy 2: Try direct item.name and item.description
        elif hasattr(item, 'name'):
            item_name = str(item.name)

            if hasattr(item, 'description'):
                item_description = str(item.description) if item.description else ''

        # Strategy 3: Try dictionary access
        elif isinstance(item, dict):
            item_name = str(item.get('name', 'Item'))
            item_description = str(item.get('description', ''))

        # Strategy 4: Check for product/item_name fields
        elif hasattr(item, 'product'):
            if hasattr(item.product, 'name'):
                item_name = str(item.product.name)
            if hasattr(item.product, 'description'):
                item_description = str(item.product.description) if item.product.description else ''

        return item_name, item_description

    except Exception as e:
        logger.error(f"Error extracting item data: {e}")
        return 'Item', ''

def fmt_qty(q):
    """
    Return a clean string:
      • 3.0  ➜  3
      • 3.25 ➜  3.25
    """
    try:
        qf = float(q)
        return str(int(qf)) if qf.is_integer() else str(qf).rstrip("0").rstrip(".")
    except (TypeError, ValueError):
        return str(q)
    
'''def generate_quote_pdf(quote, customer, items, filename, company_info, notes, totals):
    """
    Generate Quote PDF with Quantity + Unit combined in same cell
    """
    from reportlab.lib.pagesizes import A5
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    styles = getSampleStyleSheet()
    
    try:
        doc = SimpleDocTemplate(
            filename,
            pagesize=A5,
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=20
        )

        elements = []

        # Maximum available width
        page_width, _ = A5
        available_width = page_width - 40

        # Company header styles
        company_name_style = ParagraphStyle(
            'CompanyNameStyle',
            parent=styles['Heading1'],
            fontSize=14,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=0,
            spaceBefore=0,
            fontName='Helvetica-Bold'
        )

        quote_title_style = ParagraphStyle(
            'QuoteTitle',
            parent=styles['Heading2'],
            fontSize=14,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            spaceBefore=4
        )

        # Company header
        company_name = 'Sri Rama Steel & Cement'
        company_address = 'Warangal Road, Huzurabad, Telangana'
        company_contact = 'GSTIN: 36AVBPT8804D1ZJ | Ph: 8885482288, 6303417269'

        if company_info:
            company_name = company_info.get('name', company_name)
            company_address = company_info.get('address', company_address)
            phone = company_info.get('phone', '8885482288, 6303417269')
            company_contact = f'GSTIN: 36AVBPT8804D1ZJ | Ph: {phone}'

        elements.append(Paragraph(company_name, company_name_style))
        elements.append(Paragraph(company_address,
                                ParagraphStyle('Address', parent=styles['Normal'],
                                             fontSize=10, alignment=TA_CENTER)))
        elements.append(Paragraph(company_contact,
                                ParagraphStyle('Contact', parent=styles['Normal'],
                                             fontSize=10, alignment=TA_CENTER, spaceAfter=4)))

        elements.append(Paragraph('QUOTE', quote_title_style))

        # Bill To + Quote Details
        customer_name = getattr(customer, 'name', 'Customer Name')
        customer_phone = getattr(customer, 'phone', '')
        customer_address = getattr(customer, 'address', '')

        bill_to_text = customer_name
        if customer_phone:
            bill_to_text += f'\n{customer_phone}'
        if customer_address:
            bill_to_text += f'\n{customer_address}'

        # ✅ FIXED: Get quote fields (not estimate fields)
        quote_no = getattr(quote, 'quote_number')
        quote_date = getattr(quote, 'date')
        
        # Format date if it's a string
        if isinstance(quote_date, str) and len(quote_date) >= 10:
            try:
                date_obj = datetime.strptime(quote_date[:10], '%Y-%m-%d')
                quote_date = date_obj.strftime('%d/%m/%Y')
            except:
                pass

        bill_to_quote_data = [
            ['Bill To', 'Quote Details'],
            [
                bill_to_text,
                f'Quote No: {quote_no}\nQuote Date: {quote_date}'
            ]
        ]

        bill_to_quote_table = Table(bill_to_quote_data, colWidths=[available_width * 0.5, available_width * 0.5])
        bill_to_quote_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.8, 0.8, 0.8)),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 1), (-1, 1), 'LEFT'),

            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),

            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))

        elements.append(bill_to_quote_table)

        # 4-COLUMN LAYOUT with Quantity + Unit combined
        col_widths = [
            available_width * 0.15,   # Qty column
            available_width * 0.55,   # Item & Description column
            available_width * 0.15,   # Rate column
            available_width * 0.15    # Amount column
        ]

        combined_table_data = [
            ['Qty', 'Item & Description', 'Rate', 'Amount'],
        ]

        # Add items with combined Item Name + Description AND Quantity + Unit
        for item in items:
            # Get item data
            if hasattr(item, 'item'):
                item_name = getattr(item.item, 'name', 'Item')
                item_description = getattr(item.item, 'description', '')
            else:
                item_name = getattr(item, 'item_name', getattr(item, 'name', 'Item'))
                item_description = getattr(item, 'description', '')

            item_qty = getattr(item, 'quantity', 1)
            item_unit = getattr(item, 'unit', '')
            item_rate = getattr(item, 'unit_price', 0.0)
            item_amount = item_qty * item_rate

            # COMBINE ITEM NAME + DESCRIPTION
            combined_item_text = item_name
            if item_description and item_description.strip():
                combined_item_text += f'\n{item_description}'

            # COMBINE QUANTITY + UNIT in same cell
            quantity_with_unit = fmt_qty(item_qty)
            if item_unit and item_unit.strip():
                quantity_with_unit += f' {item_unit}'

            combined_table_data.append([
                quantity_with_unit,
                combined_item_text,                                  
                f'{item_rate:.2f}',
                f'{item_amount:.2f}'
            ])

        # Calculate subtotal from items
        items_subtotal = sum(getattr(item, 'quantity', 1) * getattr(item, 'unit_price', 0.0) for item in items)

        # ✅ FIXED: Always add totals, even if totals dict is empty
        calculated_subtotal = items_subtotal

        # Process totals with mandatory subtotal logic
        if totals:
            # Add other charges first
            if totals.get('hamali_charges', 0) > 0:
                calculated_subtotal += totals.get('hamali_charges', 0)
                combined_table_data.append(['Hamali Charges:', '', f'{totals.get("hamali_charges", 0):.2f}', ''])

            if totals.get('auto_charges', 0) > 0:
                calculated_subtotal += totals.get('auto_charges', 0)  
                combined_table_data.append(['Auto Charges:', '', f'{totals.get("auto_charges", 0):.2f}', ''])

            # Check for discount
            discount_amount = totals.get('discount', 0)

            # MANDATORY SUBTOTAL when discount is present
            if discount_amount > 0:
                # Always show subtotal before discount
                combined_table_data.append(['Sub Total:', '', f'{calculated_subtotal:.2f}', ''])
                combined_table_data.append(['Discount:', '', f'{discount_amount:.2f}', ''])
                final_total = calculated_subtotal - discount_amount
                combined_table_data.append(['Grand Total:', '', f'{final_total:.2f}', ''])
            else:
                # Grand Total (or just Total if no other charges)
                grand_total = totals.get('total', totals.get('grand_total', calculated_subtotal))
                combined_table_data.append(['Grand Total:', '', f'{grand_total:.2f}', ''])
        else:
            # ✅ CRITICAL FIX: If no totals dict, still show Grand Total
            combined_table_data.append(['Grand Total:', '', f'{items_subtotal:.2f}', ''])

        # Calculate table styling indices
        items_count = len(items)
        totals_start_row = items_count + 1

        combined_table = Table(combined_table_data, colWidths=col_widths)

        # Build table style
        table_style_commands = [
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.75, 0.75, 0.75)),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Items rows styling
            ('FONTNAME', (0, 1), (-1, items_count), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, items_count), 8),
            ('ALIGN', (0, 1), (0, items_count), 'LEFT'),
            ('ALIGN', (1, 1), (1, items_count), 'LEFT'),
            ('ALIGN', (2, 1), (-1, items_count), 'RIGHT'),
            ('VALIGN', (0, 1), (-1, items_count), 'TOP'),

            # Complete borders for items
            ('GRID', (0, 0), (-1, items_count), 1, colors.black),
            ('BOX', (0, 0), (-1, items_count), 1, colors.black),
        ]

        # Add totals styling if needed
        if len(combined_table_data) > items_count + 1:
            totals_end_row = len(combined_table_data) - 1

            # Merge columns for totals
            for row in range(totals_start_row, totals_end_row + 1):
                table_style_commands.append(('SPAN', (0, row), (1, row)))
                table_style_commands.append(('SPAN', (2, row), (3, row))) 

            # Style totals with selective bold formatting
            table_style_commands.extend([
            # General formatting for ALL totals rows
            ('FONTSIZE', (0, totals_start_row), (0, totals_end_row), 10),
            ('ALIGN', (0, totals_start_row), (0, totals_end_row), 'LEFT'),
            ('LEFTPADDING', (0, totals_start_row), (0, totals_end_row), 8),

            ('FONTSIZE', (2, totals_start_row), (2, totals_end_row), 10),
            ('ALIGN', (2, totals_start_row), (2, totals_end_row), 'RIGHT'),
            ('RIGHTPADDING', (2, totals_start_row), (2, totals_end_row), 8),

            # Complete borders for totals
            ('GRID', (0, totals_start_row), (-1, totals_end_row), 1, colors.black),
            ('BOX', (0, totals_start_row), (-1, totals_end_row), 1, colors.black),
            ])

            # Apply selective bold styling only to important totals (not charges)
            for i, row_data in enumerate(combined_table_data[totals_start_row:], totals_start_row):
                if row_data[0] in ['Sub Total:', 'Discount:', 'Grand Total:']:
                    table_style_commands.extend([
                        ('FONTNAME', (0, i), (0, i), 'Helvetica-Bold'),  # Bold label
                        ('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'),  # Bold amount
                    ])
                else:
                    # For charges (Hamali, Auto) - use normal weight
                    table_style_commands.extend([
                        ('FONTNAME', (0, i), (0, i), 'Helvetica'),      # Light label
                        ('FONTNAME', (2, i), (2, i), 'Helvetica'),      # Light amount
                    ])

        # Standard padding
        table_style_commands.extend([
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ])

        combined_table.setStyle(TableStyle(table_style_commands))
        elements.append(combined_table)
        
        # Build PDF with borders (like estimate)
        doc.build(elements, onFirstPage=add_refined_border, onLaterPages=add_refined_border)  # ✅ With borders


        logger.info(f"Quote PDF generated successfully: {filename}")

    except Exception as e:
        logger.error(f"Error generating Quote PDF: {str(e)}")
        raise 
    
'''


def generate_estimate_pdf(
    estimate,
    customer,
    items,
    filename,
    totals,
    company_info=None,
    notes=""
):

    """
    Generate ESTIMATE PDF with Quantity + Unit combined in same cell
    """
    try:
        doc = SimpleDocTemplate(
            filename,
            pagesize=A5,
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=20
        )

        elements = []

        # Maximum available width
        page_width, _ = A5
        available_width = page_width - 40

        # Company header styles
        company_name_style = ParagraphStyle(
            'CompanyNameStyle',
            parent=styles['Heading1'],
            fontSize=14,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=0,
            spaceBefore=0,
            fontName='Helvetica-Bold'
        )

        estimate_title_style = ParagraphStyle(
            'EstimateTitle',
            parent=styles['Heading2'],
            fontSize=14,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            spaceBefore=4
        )

        # Company header
        company_name = 'Sri Rama Steel & Cement'
        company_address = 'Warangal Road, Huzurabad, Telangana'
        company_contact = 'GSTIN: 36AVBPT8804D1ZJ | Ph: 8885482288, 6303417269'

        if company_info:
            company_name = company_info.get('name', company_name)
            company_address = company_info.get('address', company_address)
            phone = company_info.get('phone', '8885482288, 6303417269')
            company_contact = f'GSTIN: 36AVBPT8804D1ZJ | Ph: {phone}'

        elements.append(Paragraph(company_name, company_name_style))
        elements.append(Paragraph(company_address,
                                ParagraphStyle('Address', parent=styles['Normal'],
                                             fontSize=10, alignment=TA_CENTER)))
        elements.append(Paragraph(company_contact,
                                ParagraphStyle('Contact', parent=styles['Normal'],
                                             fontSize=10, alignment=TA_CENTER, spaceAfter=4)))

        elements.append(Paragraph('ESTIMATE', estimate_title_style))

        # Bill To + Estimate Details
        customer_name = customer.get("name", "Customer Name")
        customer_phone = customer.get("phone", "")
        customer_address = customer.get("address", "")

        bill_to_text = customer_name
        if customer_phone:
            bill_to_text += f'\n{customer_phone}'
        if customer_address:
            bill_to_text += f'\n{customer_address}'

        estimate_no = estimate.get("estimate_number", "EST-001")
        estimate_date = estimate.get("date", "")

        bill_to_estimate_data = [
            ['Bill To', 'Estimate Details'],
            [
                bill_to_text,
                f'Estimate No: {estimate_no}\nEstimate Date: {estimate_date}'
            ]
        ]

        bill_to_estimate_table = Table(bill_to_estimate_data, colWidths=[available_width * 0.5, available_width * 0.5])
        bill_to_estimate_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.8, 0.8, 0.8)),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 1), (-1, 1), 'LEFT'),

            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),

            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))

        elements.append(bill_to_estimate_table)

        

        # 4-COLUMN LAYOUT with Quantity + Unit combined
        col_widths = [
            available_width * 0.15,   # Item & Description column (wider)
            available_width * 0.55,   # Qty column (now includes unit)
            available_width * 0.15,   # Rate column
            available_width * 0.15    # Amount column
        ]

        combined_table_data = [
            ['Qty', 'Item & Description', 'Rate', 'Amount'],  # Same 4 columns
        ]

        

        # Add items with combined Item Name + Description AND Quantity + Unit
        item_rows_count = 0 
        for item in items:
            # ---- SKIP EMPTY / INVALID ROWS ----
            if not item.get("item_name"):
                continue

            if item.get("qty", 0) <= 0:
                continue

            if item.get("rate", 0) <= 0:
                continue

            # ---- VALID ITEM ----
            item_name = item.get("item_name", "")
            item_description = item.get("desc", "")
            item_qty = item.get("qty", 1)
            item_unit = item.get("unit", "")
            item_rate = item.get("rate", 0.0)

            item_amount = item_qty * item_rate

            combined_item_text = item_name
            if item_description.strip():
                combined_item_text += f"\n{item_description}"

            quantity_with_unit = f"{item_qty} {item_unit}"

            combined_table_data.append([
                quantity_with_unit,
                combined_item_text,
                f"{item_rate:.2f}",
                f"{item_amount:.2f}"
            ])
            item_rows_count += 1




        # ---- TOTALS BREAKDOWN ----
        items_total = totals.get("items_total", 0)
        hamali_total = totals.get("hamali_total", 0)
        auto_charge = totals.get("auto_charge", 0)
        discount = totals.get("discount", 0)

        running_total = items_total

        # Hamali row
        if hamali_total > 0:
            combined_table_data.append(['Hamali:', '', f'{hamali_total:.2f}', ''])
            running_total += hamali_total

        # Auto charge row
        if auto_charge > 0:
            combined_table_data.append(['Auto:', '', f'{auto_charge:.2f}', ''])
            running_total += auto_charge

        # Discount row (if any)
        if discount > 0:
            combined_table_data.append(['Sub Total:', '', f'{running_total:.2f}', ''])
            combined_table_data.append(['Discount:', '', f'{discount:.2f}', ''])
            running_total -= discount

        # Final total
        combined_table_data.append(['Grand Total:', '', f'{running_total:.2f}', ''])

        # Calculate table styling indices
        items_count = item_rows_count
        totals_start_row = items_count + 1  # header + item rows

        combined_table = Table(combined_table_data, colWidths=col_widths)

        # Build table style
        table_style_commands = [
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.75, 0.75, 0.75)),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Items rows styling
            ('FONTNAME', (0, 1), (-1, items_count), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, items_count), 8),
            ('ALIGN', (0, 1), (0, items_count), 'LEFT'),          # Item descriptions left
            ('ALIGN', (1, 1), (-1, items_count), 'LEFT'),        # Qty, Rate, Amount right
            ('ALIGN', (2, 1), (-1, items_count), 'RIGHT'),
            ('VALIGN', (0, 1), (-1, items_count), 'TOP'),         # Top align for multi-line

            # Complete borders for items
            ('GRID', (0, 0), (-1, items_count), 1, colors.black),
            ('BOX', (0, 0), (-1, items_count), 1, colors.black),
        ]

        # Add totals styling if needed
        if len(combined_table_data) > items_count + 1:
            totals_end_row = len(combined_table_data) - 1

            # Merge columns for totals (now spans 0-1 instead of 0-1)
            for row in range(totals_start_row, totals_end_row + 1):
                table_style_commands.append(('SPAN', (0, row), (1, row)))
                table_style_commands.append(('SPAN', (2, row), (3, row)))

            # Style totals with selective bold formatting
            table_style_commands.extend([
            # General formatting for ALL totals rows
            ('FONTSIZE', (0, totals_start_row), (0, totals_end_row), 10),
            ('ALIGN', (0, totals_start_row), (0, totals_end_row), 'LEFT'),
            ('LEFTPADDING', (0, totals_start_row), (0, totals_end_row), 8),

            ('FONTSIZE', (2, totals_start_row), (2, totals_end_row), 10),
            ('ALIGN', (2, totals_start_row), (2, totals_end_row), 'RIGHT'),
            ('RIGHTPADDING', (2, totals_start_row), (2, totals_end_row), 8),

            # Complete borders for totals
            ('GRID', (0, totals_start_row), (-1, totals_end_row), 1, colors.black),
            ('BOX', (0, totals_start_row), (-1, totals_end_row), 1, colors.black),
            ])

            # Apply selective bold styling only to important totals (not charges)
            for i, row_data in enumerate(combined_table_data[totals_start_row:], totals_start_row):
                if row_data[0] in ['Sub Total:', 'Discount:', 'Grand Total:']:
                    table_style_commands.extend([
                        ('FONTNAME', (0, i), (0, i), 'Helvetica-Bold'),  # Bold label
                        ('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'),  # Bold amount
                    ])
                else:
                    # For charges (Hamali, Auto) - use normal weight
                    table_style_commands.extend([
                        ('FONTNAME', (0, i), (0, i), 'Helvetica'),      # Light label
                        ('FONTNAME', (2, i), (2, i), 'Helvetica'),      # Light amount
                    ])

            
        # Standard padding
        table_style_commands.extend([
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ])

        combined_table.setStyle(TableStyle(table_style_commands))
        elements.append(combined_table)

        # Build PDF
        doc.build(elements, onFirstPage=add_refined_border, onLaterPages=add_refined_border)

        logger.info(f"ESTIMATE PDF generated successfully: {filename}")

    except Exception as e:
        logger.error(f"Error generating ESTIMATE PDF: {str(e)}")
        raise
