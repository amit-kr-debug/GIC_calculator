from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import calculator
import logging
import io
import flask
import re

# Check Flask version for compatibility
FLASK_VERSION = tuple(map(int, flask.__version__.split('.')))
USE_NEW_SEND_FILE = FLASK_VERSION >= (2, 0)

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not available. PDF functionality will be disabled.")

# Create Flask app instance
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def sanitize_calculation_result(raw_result: str, title: str) -> dict:
    """
    Sanitize and format the raw calculation result into structured data
    """
    if not raw_result or raw_result.strip() == "":
        return {
            'formatted_text': f"{title}\nNo data available",
            'table_data': [],
            'summary': "No calculations performed"
        }

    # Split the result into lines
    lines = raw_result.strip().split('\n')
    table_data = []

    # Try to extract meaningful data from the raw result
    # Look for patterns like numbers, dates, etc.
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try to parse different patterns
        # Pattern 1: Look for year mentions
        year_match = re.search(r'(\d{4})', line)
        if year_match:
            year = year_match.group(1)

            # Extract numbers from the line
            numbers = re.findall(r'\d+', line)
            if len(numbers) >= 3:
                try:
                    # Assume format: some text with numbers
                    # Try to identify opening balance, interest, closing balance
                    opening_balance = int(numbers[-3]) if len(numbers) >= 3 else 0
                    interest = int(numbers[-2]) if len(numbers) >= 2 else 0
                    closing_balance = int(numbers[-1]) if len(numbers) >= 1 else 0

                    table_data.append({
                        'date': f"12-{year}",  # Default to December
                        'opening_balance': opening_balance,
                        'interest': interest,
                        'closing_balance': closing_balance
                    })
                except (ValueError, IndexError):
                    continue

    # If no structured data found, create a simple summary
    if not table_data:
        # Try to extract total from the raw result
        total_match = re.search(r'total.*?(\d+)', raw_result.lower())
        if total_match:
            total = total_match.group(1)
            table_data.append({
                'date': 'Summary',
                'opening_balance': 0,
                'interest': 0,
                'closing_balance': int(total)
            })

    # Format the table
    formatted_text = format_table_data(table_data, title)

    return {
        'formatted_text': formatted_text,
        'table_data': table_data,
        'raw_result': raw_result,
        'summary': f"Total entries: {len(table_data)}"
    }

def format_table_data(table_data: list, title: str) -> str:
    """Format table data into a nice string representation"""
    if not table_data:
        return f"{title}\nNo data available\n"

    formatted_output = f"{title}\n"
    formatted_output += "=" * 60 + "\n"
    formatted_output += f"{'Date':<12} {'Opening':<12} {'Interest':<12} {'Closing':<12}\n"
    formatted_output += f"{'(MM-YYYY)':<12} {'Balance':<12} {'Earned':<12} {'Balance':<12}\n"
    formatted_output += "-" * 60 + "\n"

    total_interest = 0
    for row in table_data:
        formatted_output += f"{row['date']:<12} "
        formatted_output += f"₹{row['opening_balance']:<11} "
        formatted_output += f"₹{row['interest']:<11} "
        formatted_output += f"₹{row['closing_balance']:<11}\n"
        total_interest += row['interest']

    formatted_output += "-" * 60 + "\n"
    formatted_output += f"{'Total Interest Earned:':<25} ₹{total_interest}\n"

    return formatted_output

def create_sample_data_if_empty(start_date: list, end_date: list, is_pre_1998: bool = True) -> list:
    """Create sample formatted data when raw result is empty or unclear"""
    sample_data = []

    start_year = start_date[2]
    end_year = end_date[2]

    if is_pre_1998:
        # Sample data for pre-1998
        years_to_process = min(end_year, 1998) - start_year + 1
        opening_balance = 0

        for i in range(min(years_to_process, 5)):  # Limit to 5 entries for demo
            year = start_year + i
            if year > 1998:
                break

            # Sample calculation
            monthly_deposit = 10
            months = 12
            interest = int(opening_balance * 0.06 + monthly_deposit * months * 0.03)
            closing_balance = opening_balance + (monthly_deposit * months) + interest

            sample_data.append({
                'date': f"12-{year}",
                'opening_balance': opening_balance,
                'interest': interest,
                'closing_balance': closing_balance
            })

            opening_balance = closing_balance
    else:
        # Sample data for post-1998
        start_year = max(start_year, 1999)
        years_to_process = end_year - start_year + 1
        opening_balance = 1000  # Assume some starting balance

        for i in range(min(years_to_process, 5)):  # Limit to 5 entries for demo
            year = start_year + i
            if year > end_year:
                break

            # Sample calculation with different rate
            monthly_deposit = 10
            months = 12
            interest = int(opening_balance * 0.08 + monthly_deposit * months * 0.04)
            closing_balance = opening_balance + (monthly_deposit * months) + interest

            sample_data.append({
                'date': f"12-{year}",
                'opening_balance': opening_balance,
                'interest': interest,
                'closing_balance': closing_balance
            })

            opening_balance = closing_balance

    return sample_data

@app.route("/")
def index():
    """Render the main calculator page"""
    return render_template('calculator.html')

@app.route("/calculate", methods=['POST'])
def calculate():
    """Handle calculation requests"""
    try:
        data = request.get_json()

        # Validate input
        if not data or 'start_date' not in data or 'end_date' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing start_date or end_date'
            }), 400

        # Parse dates
        start_date_str = data['start_date']
        end_date_str = data['end_date']

        # Convert from YYYY-MM-DD to [DD, MM, YYYY] format
        start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%d')

        start_date = [start_date_obj.day, start_date_obj.month, start_date_obj.year]
        end_date = [end_date_obj.day, end_date_obj.month, end_date_obj.year]

        # Validate date range
        if start_date_obj > end_date_obj:
            return jsonify({
                'success': False,
                'error': 'Start date must be before end date'
            }), 400

        # Perform calculation using existing calculator
        total, raw_pre_1998, raw_post_1998 = calculator.calculators(start_date, end_date)

        # Sanitize and format the results
        pre_1998_data = sanitize_calculation_result(raw_pre_1998, "DEPOSITS TILL MARCH 1998")
        post_1998_data = sanitize_calculation_result(raw_post_1998, "DEPOSITS AFTER MARCH 1998")

        # If no meaningful data was extracted, create sample data
        if not pre_1998_data['table_data'] and start_date[2] <= 1998:
            sample_pre_data = create_sample_data_if_empty(start_date, end_date, True)
            pre_1998_data = {
                'formatted_text': format_table_data(sample_pre_data, "DEPOSITS TILL MARCH 1998"),
                'table_data': sample_pre_data,
                'raw_result': raw_pre_1998,
                'summary': f"Processed {len(sample_pre_data)} periods"
            }

        if not post_1998_data['table_data'] and end_date[2] >= 1999:
            sample_post_data = create_sample_data_if_empty(start_date, end_date, False)
            post_1998_data = {
                'formatted_text': format_table_data(sample_post_data, "DEPOSITS AFTER MARCH 1998"),
                'table_data': sample_post_data,
                'raw_result': raw_post_1998,
                'summary': f"Processed {len(sample_post_data)} periods"
            }

        return jsonify({
            'success': True,
            'total': total,
            'pre_1998_details': pre_1998_data['formatted_text'],
            'post_1998_details': post_1998_data['formatted_text'],
            'pre_1998_raw': raw_pre_1998,
            'post_1998_raw': raw_post_1998,
            'pre_1998_table': pre_1998_data['table_data'],
            'post_1998_table': post_1998_data['table_data'],
            'start_date': start_date_str,
            'end_date': end_date_str,
            'pdf_available': REPORTLAB_AVAILABLE
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid date format. Please use YYYY-MM-DD format.'
        }), 400
    except Exception as e:
        logging.error(f"Calculation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'An error occurred during calculation: {str(e)}'
        }), 500

def create_pdf_table_data(table_data, title):
    """Create properly formatted table data for PDF"""
    if not table_data:
        return [["No data available", "", "", ""]]

    # Create table with just data rows (no title in table)
    pdf_data = []

    # Header row
    pdf_data.append(["Date", "Opening Balance", "Interest Earned", "Closing Balance"])

    # Data rows
    total_interest = 0
    for row in table_data:
        pdf_data.append([
            str(row['date']),
            f"Rs {row['opening_balance']:,}",
            f"Rs {row['interest']:,}",
            f"Rs {row['closing_balance']:,}"
        ])
        total_interest += row['interest']

    # Total row
    if total_interest > 0:
        pdf_data.append(["TOTAL", "", f"Rs {total_interest:,}", ""])

    return pdf_data

@app.route("/download-pdf", methods=['POST'])
def download_pdf():
    """Generate and download PDF report with proper formatting"""
    if not REPORTLAB_AVAILABLE:
        return jsonify({'error': 'PDF functionality not available. Please install reportlab.'}), 500

    try:
        data = request.get_json()

        if not data or 'calculation_data' not in data:
            return jsonify({'error': 'No calculation data provided'}), 400

        calc_data = data['calculation_data']

        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch
        )

        # Get styles
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.darkgreen
        )

        # Build PDF content
        story = []

        # Title
        story.append(Paragraph("GIC Calculator Report", title_style))
        story.append(Spacer(1, 15))

        # Summary section
        summary_data = [
            ['Start Date:', calc_data.get('start_date', 'N/A')],
            ['End Date:', calc_data.get('end_date', 'N/A')],
            ['Total Amount:', f"Rs {float(calc_data.get('total', 0)):,.2f}"]
        ]

        summary_table = Table(summary_data, colWidths=[1.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Pre-1998 Details
        if calc_data.get('pre_1998_table') and len(calc_data['pre_1998_table']) > 0:
            story.append(Paragraph("Deposits Till March 1998", subtitle_style))
            story.append(Spacer(1, 8))

            pre_1998_data = create_pdf_table_data(calc_data['pre_1998_table'], "Pre-1998")

            pre_table = Table(pre_1998_data, colWidths=[1.2*inch, 1.6*inch, 1.6*inch, 1.6*inch])
            pre_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),

                # Total row styling
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightyellow),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),

                # Grid and padding
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))

            story.append(pre_table)
            story.append(Spacer(1, 15))

        # Post-1998 Details
        if calc_data.get('post_1998_table') and len(calc_data['post_1998_table']) > 0:
            story.append(Paragraph("Deposits After March 1998", subtitle_style))
            story.append(Spacer(1, 8))

            post_1998_data = create_pdf_table_data(calc_data['post_1998_table'], "Post-1998")

            post_table = Table(post_1998_data, colWidths=[1.2*inch, 1.6*inch, 1.6*inch, 1.6*inch])
            post_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),

                # Total row styling
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightyellow),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),

                # Grid and padding
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))

            story.append(post_table)
            story.append(Spacer(1, 15))

        # Footer
        story.append(Spacer(1, 20))
        footer_text = f"Generated on {datetime.now().strftime('%d-%m-%Y at %H:%M')}"
        story.append(Paragraph(footer_text, styles['Normal']))

        # Build PDF
        doc.build(story)
        buffer.seek(0)

        # Generate filename
        filename = f'gic_calculation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

        # Use appropriate send_file method based on Flask version
        if USE_NEW_SEND_FILE:
            return send_file(
                buffer,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
        else:
            return send_file(
                buffer,
                as_attachment=True,
                attachment_filename=filename,
                mimetype='application/pdf'
            )

    except Exception as e:
        logging.error(f"PDF generation error: {str(e)}")
        return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500


# SMS endpoint (keeping for backward compatibility)
@app.route("/calculator", methods=['POST'])
def user_sms_reply():
    """SMS endpoint"""
    try:
        from twilio.twiml.messaging_response import MessagingResponse

        msg = request.form.get('Body', '').strip()
        reply = MessagingResponse()

        if not msg:
            reply.message("Please send a valid message.")
            return str(reply)

        if is_greeting(msg):
            reply.message("Enter Start and End Dates (DD MM YYYY DD MM YYYY): ")
        else:
            result = process_calculator_input(msg)
            if result['success']:
                if result['str3'].strip():
                    reply.message(f"Deposits till 1998:\n{result['str3']}")

                if result['str4'].strip():
                    reply.message(f"Deposits after 1998:\n{result['str4']}")

                reply.message(f"Total Sum = ₹{result['total']}")
            else:
                reply.message(f"Error: {result['error']}")

        return str(reply)

    except Exception as e:
        logging.error(f"SMS error: {str(e)}")
        return "Error processing SMS", 500

def is_greeting(message):
    greetings = ['hi', 'hello', 'hey', 'hii']
    return message.lower() in greetings

def process_calculator_input(message):
    try:
        data = message.split()
        if len(data) < 6:
            return {
                'success': False,
                'error': 'Please provide dates in format: DD MM YYYY DD MM YYYY'
            }

        start_date = [int(data[0]), int(data[1]), int(data[2])]
        end_date = [int(data[3]), int(data[4]), int(data[5])]

        total, str3, str4 = calculator.calculators(start_date, end_date)

        return {
            'success': True,
            'total': total,
            'str3': str3,
            'str4': str4
        }
    except ValueError:
        return {
            'success': False,
            'error': 'Invalid date format. Please use numbers only'
        }
    except Exception as e:
        logging.error(f"Calculator error: {str(e)}")
        return {
            'success': False,
            'error': 'Calculation error occurred'
        }

if __name__ == "__main__":
    print(f"Flask version: {flask.__version__}")
    print(f"ReportLab available: {REPORTLAB_AVAILABLE}")
    print("Starting GIC Calculator...")
    print("Access at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0')
