import json
import os
import logging
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from num2words import num2words

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemplateManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.load_settings()
        logger.info("Template Manager initialized")

    def load_settings(self):
        try:
            config_path = os.path.join(self.base_dir, 'config', 'template_settings.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.settings = json.load(f)
                    logger.info("Settings loaded from %s", config_path)
            else:
                self.settings = {
                    'template': 'Simple',
                    'logo_path': '',
                    'primary_color': '#000000',
                    'font': 'Arial',
                    'footer_text': '',
                    'show_tax': True,
                    'show_discount': True,
                    'show_transport': False,
                    'show_terms': True,
                    'show_signature': False,
                    'company_name': 'SRI RAMA STEEL AND CEMENT',
                    'company_address': 'opposite TVS showroom, Warangal road, Huzurabad.',
                    'company_phone': '8885482288',
                    'company_gstin': '36AVBPT8804D1ZJ',
                    'company_state': '36-Telangana'
                }
                # Create config directory if it doesn't exist
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                # Save default settings
                with open(config_path, 'w') as f:
                    json.dump(self.settings, f, indent=4)
                logger.info("Created default settings at %s", config_path)
        except Exception as e:
            logger.error("Error loading template settings: %s", str(e))
            self.settings = {}

    def get_template_style(self):
        styles = getSampleStyleSheet()
        
        # Convert hex color to RGB
        color_hex = self.settings.get('primary_color', '#2196F3').lstrip('#')
        primary_color = colors.Color(
            int(color_hex[:2], 16) / 255,
            int(color_hex[2:4], 16) / 255,
            int(color_hex[4:], 16) / 255
        )

        # Create custom styles
        styles.add(ParagraphStyle(
            name='CompanyName',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=primary_color,
            spaceAfter=10
        ))

        styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=primary_color,
            spaceAfter=8
        ))

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

        return styles

    def create_header(self, doc, estimate_info):
        elements = []
        styles = self.get_template_style()

        # Company name in bold
        elements.append(Paragraph(self.settings.get('company_name', 'SRI RAMA STEEL AND CEMENT'), ParagraphStyle(
            'CompanyName',
            parent=styles['Normal'],
            fontSize=20,
            fontName='Helvetica-Bold',
            alignment=1,  # Center alignment
            spaceAfter=6  # Increased spacing after company name
        )))
        
        # Add a small spacer
        elements.append(Spacer(1, 2 * mm))
        
        # Company address
        elements.append(Paragraph(self.settings.get('company_address', ''), ParagraphStyle(
            'Address',
            parent=styles['Normal'],
            fontSize=14,
            fontName='Helvetica',
            alignment=1,  # Center alignment
            spaceAfter=2
        )))
        
        # Company phone
        elements.append(Paragraph(self.settings.get('company_phone', ''), ParagraphStyle(
            'Phone',
            parent=styles['Normal'],
            fontSize=14,
            fontName='Helvetica',
            alignment=1,  # Center alignment
            spaceAfter=2
        )))
        
        # Company GSTIN
        elements.append(Paragraph(self.settings.get('company_gstin', ''), ParagraphStyle(
            'GSTIN',
            parent=styles['Normal'],
            fontSize=14,
            fontName='Helvetica',
            alignment=1,  # Center alignment
            spaceAfter=2
        )))
        
        # Company State
        elements.append(Paragraph(self.settings.get('company_state', ''), ParagraphStyle(
            'State',
            parent=styles['Normal'],
            fontSize=14,
            fontName='Helvetica',
            alignment=1,  # Center alignment
            spaceAfter=6
        )))
        
        # Add horizontal line
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            lineCap='round',
            color=colors.black,
            spaceBefore=1,
            spaceAfter=6
        ))

        # Create two-column layout for Bill To and Estimate Details
        bill_to = Paragraph("Bill To", ParagraphStyle(
            'SectionHeading',
            parent=styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            spaceAfter=1
        ))
        estimate_title = Paragraph("Estimate Details", ParagraphStyle(
            'SectionHeading',
            parent=styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            spaceAfter=1
        ))
        
        # Get customer details directly from the parameter
        customer = estimate_info.get('customer', {})
        
        # Create Bill To section with customer details in specified order
        customer_details = []
        
        # 1. Customer Name (in bold)
        if customer.get('name'):
            customer_details.append(Paragraph(customer['name'], ParagraphStyle(
                'CustomerName',
                parent=styles['Normal'],
                fontSize=13,
                fontName='Helvetica-Bold',
                spaceAfter=2
            )))
        
        # 2. Contact Number
        if customer.get('phone'):
            customer_details.append(Paragraph(f"{customer['phone']}", ParagraphStyle(
                'CustomerPhone',
                parent=styles['Normal'],
                fontSize=13,
                fontName='Helvetica',
                spaceAfter=2
            )))
        
        # 3. Address with city and state
        address_parts = []
        if customer.get('address'):
            address_parts.append(customer['address'])
        if customer.get('city') and customer.get('state'):
            address_parts.append(f"{customer['city']}, {customer['state']}")
        elif customer.get('city'):
            address_parts.append(customer['city'])
        elif customer.get('state'):
            address_parts.append(customer['state'])
            
        if address_parts:
            customer_details.append(Paragraph(
                "\n".join(address_parts),
                ParagraphStyle(
                    'CustomerAddress',
                    parent=styles['Normal'],
                    fontSize=13,
                    fontName='Helvetica',
                    spaceAfter=2,
                    leading=13  # Adjust line spacing for address
                )
            ))
        
        # 4. Remaining details (GSTIN, Email)
        if customer.get('gstin'):
            customer_details.append(Paragraph(f"GSTIN: {customer['gstin']}", ParagraphStyle(
                'CustomerGSTIN',
                parent=styles['Normal'],
                fontSize=13,
                fontName='Helvetica',
                spaceAfter=2
            )))
        
        if customer.get('email'):
            customer_details.append(Paragraph(f"Email: {customer['email']}", ParagraphStyle(
                'CustomerEmail',
                parent=styles['Normal'],
                fontSize=13,
                fontName='Helvetica',
                spaceAfter=2
            )))
            
        # If no customer details, add placeholder
        if not customer_details:
            customer_details.append(Paragraph("No customer details available", styles['Normal']))
        
        # Create estimate details section
        estimate_details = [
            Paragraph(f"Estimate No: {estimate_info.get('est_no', '')}", styles['Normal']),
            Paragraph(f"Date: {estimate_info.get('date', '')}", styles['Normal'])
        ]
        
        # Create table data
        table_data = [[bill_to, estimate_title]]
        max_rows = max(len(customer_details), len(estimate_details))
        
        # Add customer and estimate details
        for i in range(max_rows):
            customer_cell = customer_details[i] if i < len(customer_details) else Paragraph("", styles['Normal'])
            estimate_cell = estimate_details[i] if i < len(estimate_details) else Paragraph("", styles['Normal'])
            table_data.append([customer_cell, estimate_cell])
        
        # Create table
        col_width = doc.width / 2.2  # Slightly less than half to account for spacing
        details_table = Table(table_data, colWidths=[col_width, col_width])
        
        # Style the table
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Headers in bold
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),  # Space after headers
            ('TOPPADDING', (0, 1), (-1, -1), 0),    # No top padding for details
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2),  # Minimal padding between detail lines
            ('LEFTPADDING', (0, 0), (-1, -1), 4),   # Left padding for all cells
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),  # Right padding for all cells
        ]))
        
        elements.append(details_table)
        elements.append(Spacer(1, 5 * mm))  # Space before items table
        
        return elements

    def create_customer_section(self, customer):
        # Customer details are now integrated into the Bill To section
        return []
        elements.append(Spacer(1, 10 * mm))
        
        return elements

    def create_items_table(self, items, doc):
        """Create the items table section."""
        try:
            styles = self.get_template_style()

            # Define column headers and widths
            headers = ['Item & Description', 'Qty', 'Unit', 'Rate', 'Amount']
            col_widths = [
                doc.width * 0.4,  # Item & Description (40%)
                doc.width * 0.1,  # Qty (10%)
                doc.width * 0.15, # Unit (15%)
                doc.width * 0.15, # Rate (15%)
                doc.width * 0.15  # Amount (15%)
            ]

            # Create table data starting with headers
            table_data = [[
                Paragraph(header, ParagraphStyle(
                    'Header',
                    parent=styles['Normal'],
                    fontSize=13,
                    fontName='Helvetica-Bold',
                    alignment=TA_CENTER
                )) for header in headers
            ]]

            # Add items
            items_subtotal = 0
            for item in items:
                # Handle both dictionary and object access
                if isinstance(item, dict):
                    name = item.get('name', '')
                    description = item.get('description', '')
                    quantity = item.get('quantity', 0)
                    unit = item.get('unit', '')
                    rate = item.get('rate', 0)
                    amount = item.get('amount', quantity * rate)
                else:
                    name = item.item.name if hasattr(item, 'item') else ''
                    description = item.item.description if hasattr(item, 'item') else ''
                    quantity = item.quantity if hasattr(item, 'quantity') else 0
                    unit = item.unit if hasattr(item, 'unit') else ''
                    rate = item.unit_price if hasattr(item, 'unit_price') else 0
                    amount = quantity * rate

                # Create item name and description with different styles
                item_text = [
                    Paragraph(name, ParagraphStyle(
                        'ItemName',
                        parent=styles['Normal'],
                        fontSize=13,
                        fontName='Helvetica',
                        alignment=TA_LEFT,
                        leading=13
                    ))
                ]
                
                if description:
                    item_text.append(
                        Paragraph(description, ParagraphStyle(
                            'ItemDescription',
                            parent=styles['Normal'],
                            fontSize=8,  # Smaller font for description
                            fontName='Helvetica',
                            alignment=TA_LEFT,
                            leading=10,
                            textColor=colors.gray  # Gray color for description
                        ))
                    )
                
                row = [
                    item_text,  # List of Paragraphs for name and description
                    Paragraph(str(quantity), ParagraphStyle(
                        'Number',
                        parent=styles['Normal'],
                        fontSize=13,
                        fontName='Helvetica',
                        alignment=TA_RIGHT
                    )),
                    Paragraph(unit, ParagraphStyle(
                        'Unit',
                        parent=styles['Normal'],
                        fontSize=13,
                        fontName='Helvetica',
                        alignment=TA_CENTER
                    )),
                    Paragraph(f"{rate:,.2f}", ParagraphStyle(
                        'Number',
                        parent=styles['Normal'],
                        fontSize=13,
                        fontName='Helvetica',
                        alignment=TA_RIGHT
                    )),
                    Paragraph(f"{amount:,.2f}", ParagraphStyle(
                        'Number',
                        parent=styles['Normal'],
                        fontSize=13,
                        fontName='Helvetica',
                        alignment=TA_RIGHT
                    ))
                ]
                table_data.append(row)
                items_subtotal += amount

            # Create table
            items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            # Define table style
            style = TableStyle([
                # Headers
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
                
                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ])
            
            # Add alternating row colors
            for i in range(1, len(table_data)):
                if i % 2 == 0:
                    style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
            
            items_table.setStyle(style)
            return items_table

        except Exception as e:
            logger.error(f"Error in create_items_table: {str(e)}")
            return None

    def create_totals_section(self, totals, doc):
        """Create the totals section of the document."""
        try:
            elements = []
            styles = self.get_template_style()

            # Calculate totals
            subtotal = totals.get('subtotal', 0)
            hamali_charges = totals.get('hamali_charges', 0)
            auto_charges = totals.get('auto_charges', 0)
            discount_type = totals.get('discount_type', 'flat')
            discount_value = totals.get('discount_value', 0)
            total_amount = totals.get('total_amount', 0)

            # Create totals table data
            totals_data = []
            
            # Show auto charges first if non-zero
            if auto_charges > 0:
                totals_data.append(['Auto Charges:', f"{auto_charges:,.2f}"])
            
            # Show hamali charges if non-zero
            if hamali_charges > 0:
                totals_data.append(['Hamali Charges:', f"{hamali_charges:,.2f}"])
            
            # Show subtotal after charges
            totals_data.append(['Subtotal:', f"{subtotal:,.2f}"])
            
            # Only show discount if non-zero
            if discount_value > 0:
                discount_label = f"Discount ({discount_value}%)" if discount_type == 'percentage' else 'Discount'
                discount_amount = (subtotal * discount_value / 100) if discount_type == 'percentage' else discount_value
                totals_data.append([
                    Paragraph(discount_label, ParagraphStyle(
                        'DiscountLabel',
                        parent=styles['Normal'],
                        fontSize=13,
                        fontName='Helvetica-Bold',
                        alignment=TA_RIGHT
                    )),
                    f"{discount_amount:,.2f}"
                ])
            
            # Always show grand total
            totals_data.append([
                Paragraph('Grand Total:', ParagraphStyle(
                    'GrandTotalLabel',
                    parent=styles['Normal'],
                    fontSize=13,
                    fontName='Helvetica-Bold',
                    alignment=TA_RIGHT
                )),
                Paragraph(f"{total_amount:,.2f}", ParagraphStyle(
                    'GrandTotalAmount',
                    parent=styles['Normal'],
                    fontSize=13,
                    fontName='Helvetica-Bold',
                    alignment=TA_RIGHT
                ))
            ])

            # Calculate column widths based on page width
            available_width = doc.width
            label_width = available_width * 0.7  # 70% for labels
            amount_width = available_width * 0.3  # 30% for amounts

            # Create table
            totals_table = Table(totals_data, colWidths=[label_width, amount_width])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # Right align labels
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Right align amounts
                ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),  # Regular font for all rows except last
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),  # Line above Grand Total
            ]))

            elements.append(totals_table)
            elements.append(Spacer(1, 5 * mm))

            # Add amount in words
            amount_in_words = num2words(int(total_amount), lang='en_IN').title()
            paise = int((total_amount % 1) * 100)
            if paise > 0:
                amount_in_words += f" And {num2words(paise, lang='en_IN')} Paise"
            amount_in_words += " Only"

            elements.append(Paragraph("Amount In Words:", ParagraphStyle(
                'AmountTitle',
                parent=styles['Normal'],
                fontSize=10,
                fontName='Helvetica-Bold'
            )))
            elements.append(Paragraph(amount_in_words, ParagraphStyle(
                'AmountWords',
                parent=styles['Normal'],
                fontSize=10,
                fontName='Helvetica',
                leading=14
            )))

            return elements

        except Exception as e:
            logger.error(f"Error in create_totals_section: {str(e)}")
            return []

    def create_footer(self, totals):
        """Create the footer section of the document."""
        try:
            elements = []
            styles = self.get_template_style()

            # Add notes if present
            if totals.get('note'):
                elements.append(Spacer(1, 5 * mm))
                elements.append(Paragraph("Notes:", ParagraphStyle(
                    'NotesTitle',
                    parent=styles['Normal'],
                    fontSize=10,
                    fontName='Helvetica-Bold'
                )))
                elements.append(Paragraph(totals['note'], ParagraphStyle(
                    'Notes',
                    parent=styles['Normal'],
                    fontSize=10,
                    fontName='Helvetica',
                    leading=14
                )))
            
            # Add Terms and Conditions
            if self.settings.get('show_terms', True) and self.settings.get('terms_and_conditions'):
                elements.append(Spacer(1, 5 * mm))
                elements.append(Paragraph("Terms and Conditions:", ParagraphStyle(
                    'TermsTitle',
                    parent=styles['Normal'],
                    fontSize=10,
                    fontName='Helvetica-Bold'
                )))
                terms_text = "<br/>".join(self.settings['terms_and_conditions'])
                elements.append(Paragraph(terms_text, ParagraphStyle(
                    'Terms',
                    parent=styles['Normal'],
                    fontSize=9,
                    fontName='Helvetica',
                    leading=13
                )))

            # Add Bank Details
            if self.settings.get('bank_details'):
                elements.append(Spacer(1, 5 * mm))
                elements.append(Paragraph("Bank Details:", ParagraphStyle(
                    'BankTitle',
                    parent=styles['Normal'],
                    fontSize=10,
                    fontName='Helvetica-Bold'
                )))
                bank_details = self.settings['bank_details']
                bank_text = f"""
                Bank Name: {bank_details.get('bank_name', '')}<br/>
                Account Name: {bank_details.get('account_name', '')}<br/>
                Account Number: {bank_details.get('account_number', '')}<br/>
                IFSC Code: {bank_details.get('ifsc_code', '')}<br/>
                Branch: {bank_details.get('branch', '')}
                """
                elements.append(Paragraph(bank_text, ParagraphStyle(
                    'BankDetails',
                    parent=styles['Normal'],
                    fontSize=9,
                    fontName='Helvetica',
                    leading=13
                )))
            
            # Add signature section if enabled
            if self.settings.get('show_signature', False):
                elements.append(Spacer(1, 15 * mm))
                signature_data = [
                    ['', ''],
                    ['_____________________', '_____________________'],
                    ['Authorized Signature', 'Customer Signature']
                ]
                # Calculate signature width based on A4 page width minus margins
                signature_width = (210 - 40) * mm / 2  # A4 width (210mm) - margins (40mm) / 2
                signature_table = Table(signature_data, colWidths=[signature_width, signature_width])
                signature_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 2), (-1, 2), 'Helvetica'),
                    ('FONTSIZE', (0, 2), (-1, 2), 10),
                    ('TOPPADDING', (0, 2), (-1, 2), 5),
                ]))
                elements.append(signature_table)

            return elements

        except Exception as e:
            logger.error(f"Error creating footer: {str(e)}")
            return []

    def apply_template(self, doc, elements):
        """Build the document with the provided elements."""
        try:
            if not elements:
                raise ValueError("No elements to build document")
            
            # Build document with the flat list of elements
            doc.build(elements)
        except Exception as e:
            logger.error(f"Error building document: {str(e)}")
            raise
            
    def _update_element(self, element, doc):
        """Helper method to update elements with doc parameter if needed."""
        # This method is unused now that we're passing doc to each section creator
        return element

    def create_pdf(self, doc, estimate_info, customer_info, items, totals):
        """Create the PDF document with all sections."""
        try:
            elements = []
            
            # Add header
            header_elements = self.create_header(doc, estimate_info)
            if header_elements:
                elements.extend(header_elements)
                elements.append(Spacer(1, 5 * mm))

            # Add items table
            items_table = self.create_items_table(items, doc)
            if items_table:
                elements.append(items_table)
                elements.append(Spacer(1, 5 * mm))

            # Add totals section
            totals_elements = self.create_totals_section(totals, doc)
            if totals_elements:
                elements.extend(totals_elements)
            
            # Build the document
            self.apply_template(doc, elements)
            
        except Exception as e:
            logger.error(f"Error creating PDF: {str(e)}")
            raise

    def generate_estimate_pdf(self, estimate, customer, items, filename, company_info, notes, totals):
        """Generate a PDF estimate."""
        try:
            # Update settings with company info
            if company_info:
                self.settings.update(company_info)
            
            # Add notes to estimate info
            if notes:
                estimate['notes'] = notes

            # Ensure customer details are in estimate_info
            if 'customer' not in estimate:
                estimate['customer'] = customer
            
            # Create the PDF document
            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                rightMargin=20 * mm,
                leftMargin=20 * mm,
                topMargin=20 * mm,
                bottomMargin=20 * mm
            )
            
            # Create the PDF with all sections
            self.create_pdf(doc, estimate, customer, items, totals)
            
            logger.info(f"PDF generated successfully: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise 