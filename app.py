import datetime
from flask import Flask, render_template, redirect, url_for, session, flash, request, send_from_directory
from flask_wtf import FlaskForm
from datetime import datetime, date
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, FileField, TextAreaField, DateField, TimeField
from wtforms.validators import Length, DataRequired, Email, ValidationError, InputRequired, NumberRange
import bcrypt
from flask_mysqldb import MySQL
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import TimeField
from wtforms import SelectField, FloatField, TimeField
from flask import jsonify, request
from flask_mail import Mail, Message
import random
from fpdf import FPDF
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads' 
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'samiulhaquebondhon0@gmail.com'
app.config['MAIL_PASSWORD'] = 'tkqn ngtf sgng lpbm'
app.config['MAIL_DEFAULT_SENDER'] = ('University Transport System', app.config['MAIL_USERNAME'])

mail = Mail(app)



app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root'     
app.config['MYSQL_PASSWORD'] = ''       
app.config['MYSQL_DB'] = 'mydatabase'  
app.secret_key = 'your_secret_key_here'

mysql = MySQL(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def future_date(form, field):
    if field.data <= date.today():
        raise ValidationError("Journey date must be in the future.")

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/download_ticket/<int:booking_id>')
def download_ticket(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    # Fetch booking details
    cursor.execute("""
        SELECT 
            sb.booking_id,
            sb.user_id,
            sb.route_id,
            sb.stop_id,
            sb.trip_id,
            sb.seat_number,
            sb.journey_type,
            sb.journey_date,
            sb.shift,
            sb.payment_method,
            br.route_name,
            rs.stop_name,
            u.name,
            u.student_id,
            u.department
        FROM seat_bookings sb
        JOIN bus_routes br ON sb.route_id = br.route_id
        JOIN route_stops rs ON sb.stop_id = rs.stop_id
        JOIN users u ON sb.user_id = u.id
        WHERE sb.booking_id = %s AND sb.user_id = %s
    """, (booking_id, user_id))
    
    booking = cursor.fetchone()
    cursor.close()

    if not booking:
        flash('Ticket not found', 'danger')
        return redirect(url_for('dashboard'))

    user_details = {
        'name': booking[12],      # u.name
        'student_id': booking[13], # u.student_id
        'department': booking[14]  # u.department
    }

    booking_details = {
        'journey_type': booking[6],  # sb.journey_type
        'journey_date': booking[7],  # sb.journey_date
        'shift': booking[8],         # sb.shift
        'seat_number': booking[5]    # sb.seat_number
    }

    route_details = {
        'route_name': booking[10],  # br.route_name
        'stop_name': booking[11]    # rs.stop_name
    }

    # Generate PDF
    filename = generate_ticket_pdf(user_details, booking_details, route_details)

    # Return the PDF file
    return send_from_directory(
        os.path.join(app.config['UPLOAD_FOLDER'], 'tickets'),
        filename,
        as_attachment=True
    )

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user_id' not in session or 'pending_booking' not in session:
        flash("Payment session expired. Please select your seat again.", "danger")
        return redirect(url_for('dashboard'))

    booking_details = session.get('pending_booking')
    cursor = mysql.connection.cursor()

    # Fetch fare from route_stops table
    cursor.execute("""
        SELECT fare
        FROM route_stops
        WHERE stop_id = %s
    """, (booking_details['stop_id'],))
    fare = cursor.fetchone()
    fare = fare[0] if fare else 50.00  # Default to 50 if fare not found

    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        try:
            # Final check for seat availability
            cursor.execute("""
                SELECT seat_number
                FROM seat_bookings
                WHERE route_id = %s AND stop_id = %s AND seat_number = %s AND journey_date = %s AND shift = %s
            """, (booking_details['route_id'], booking_details['stop_id'], 
                  booking_details['seat_number'], date.today(), booking_details['shift']))
            already_reserved = cursor.fetchone()
            
            if already_reserved:
                return jsonify({
                    'status': 'error',
                    'message': 'The selected seat has already been booked. Please choose another seat.'
                })

            # Get trip_id
            cursor.execute("""
                SELECT trip_id FROM trip_times WHERE stop_id = %s AND shift = %s
            """, (booking_details['stop_id'], booking_details['shift']))
            trip_id = cursor.fetchone()[0]

            # Insert booking
            cursor.execute("""
                INSERT INTO seat_bookings 
                (user_id, route_id, stop_id, trip_id, seat_number, journey_type, journey_date, shift, payment_method)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (session['user_id'], booking_details['route_id'], booking_details['stop_id'], 
                  trip_id, booking_details['seat_number'], booking_details['journey_type'], 
                  date.today(), booking_details['shift'], payment_method))
            
            booking_id = cursor.lastrowid
            
            # Insert payment record
            cursor.execute("""
                INSERT INTO payment_records 
                (booking_id, user_id, payment_method, amount)
                VALUES (%s, %s, %s, %s)
            """, (booking_id, session['user_id'], payment_method, fare))
            
            mysql.connection.commit()
            flash(f"Payment successful! Fare: {fare} TK", "success")
            return jsonify({
                'status': 'success',
                'message': f'Payment successful! Fare: {fare} TK',
                'redirect': url_for('dashboard')
            })
            
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
            cursor.close()

    # For GET requests, render the payment page with fare
    cursor.close()
    return render_template('payment.html', fare=fare)


@app.route('/complete_payment', methods=['POST'])
def complete_payment():
    if 'user_id' not in session or 'pending_booking' not in session:
        return jsonify({'status': 'error', 'message': 'Session expired'})
    
    payment_password = request.form.get('password')  # This is the payment password
    payment_number = session.get('payment_mobile')   # Get the stored mobile number
    booking_details = session.get('pending_booking')
    payment_method = session.get('payment_method')

    cursor = mysql.connection.cursor()

    try:
        cursor.execute("""
            SELECT fare
            FROM route_stops
            WHERE stop_id = %s
        """, (booking_details['stop_id'],))
        fare = cursor.fetchone()
        fare = fare[0] if fare else 50.00
        # Get trip_id
        cursor.execute("""
            SELECT trip_id FROM trip_times 
            WHERE stop_id = %s AND shift = %s
        """, (booking_details['stop_id'], booking_details['shift']))
        trip_id = cursor.fetchone()[0]

        # Insert booking
        cursor.execute("""
            INSERT INTO seat_bookings 
            (user_id, route_id, stop_id, trip_id, seat_number, journey_type, journey_date, shift, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            booking_details['route_id'],
            booking_details['stop_id'],
            trip_id,
            booking_details['seat_number'],
            booking_details['journey_type'],
            date.today(),
            booking_details['shift'],
            payment_method
        ))
        
        booking_id = cursor.lastrowid

        # Get user details
        cursor.execute("""
            SELECT name, email, student_id, department 
            FROM users 
            WHERE id = %s
        """, (session['user_id'],))
        user_details = cursor.fetchone()

        # Insert payment record with the mobile number, not the password
        cursor.execute("""
            INSERT INTO payment_records 
            (booking_id, user_id, name, email, student_id, department, payment_method, payment_number, amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            booking_id,
            session['user_id'],
            user_details[0],
            user_details[1],
            user_details[2],
            user_details[3],
            payment_method,
            payment_number,  # Use the stored mobile number
            fare  # Use the fare fetched from the route_stops table
        ))
        
        mysql.connection.commit()
        
        # Clear session data
        session.pop('otp', None)
        session.pop('booking_details', None)
        session.pop('pending_booking', None)
        session.pop('payment_method', None)
        session.pop('payment_otp', None)
        session.pop('payment_mobile', None)
        
        return jsonify({
            'status': 'success',
            'message': 'Payment successful! Your ticket has been booked.',
            'redirect': url_for('dashboard')
        })
        
    except Exception as e:
        mysql.connection.rollback()
        print(f"Payment Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        cursor.close()

@app.route('/cancel_ticket/<int:booking_id>', methods=['POST'])
def cancel_ticket(booking_id):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Please login first'})

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    try:
        # Get ticket and payment details before deletion
        cursor.execute("""
            SELECT sb.payment_method, pr.payment_number, pr.amount
            FROM seat_bookings sb
            JOIN payment_records pr ON sb.booking_id = pr.booking_id
            WHERE sb.booking_id = %s AND sb.user_id = %s
        """, (booking_id, user_id))
        ticket_details = cursor.fetchone()
        
        if not ticket_details:
            return jsonify({'status': 'error', 'message': 'Ticket not found'})
        
        # Store payment details in session for refund process
        session['refund_details'] = {
            'payment_method': ticket_details[0],
            'payment_number': ticket_details[1],
            'amount': float(ticket_details[2]),
            'booking_id': booking_id
        }
        
        # Delete records
        cursor.execute("DELETE FROM payment_records WHERE booking_id = %s", (booking_id,))
        cursor.execute("DELETE FROM seat_bookings WHERE booking_id = %s", (booking_id,))
        
        mysql.connection.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Ticket cancelled successfully',
            'html': render_template('refund_mobile_popup.html', payment_method=ticket_details[0])
        })
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        cursor.close()

@app.route('/verify_refund_mobile', methods=['POST'])
def verify_refund_mobile():
    if 'refund_details' not in session:
        return jsonify({'status': 'error', 'message': 'Refund session expired'})
    
    mobile = request.form.get('mobile')
    payment_method = session['refund_details']['payment_method']
    
    # Store mobile number in session
    session['refund_mobile'] = mobile
    
    # Generate OTP
    otp = generate_otp()
    session['refund_otp'] = otp
    
    return jsonify({
        'status': 'success',
        'message': f'OTP sent to {mobile}',
        'demo_otp': otp,  # Keep this for demonstration
        'html': render_template('refund_otp_popup.html', payment_method=payment_method)
    })

@app.route('/process_refund', methods=['POST'])
def process_refund():
    if 'refund_details' not in session:
        return jsonify({'status': 'error', 'message': 'Refund session expired'})
    
    entered_otp = request.form.get('otp')
    stored_otp = session.get('refund_otp')
    
    if entered_otp != stored_otp:
        return jsonify({'status': 'error', 'message': 'Invalid OTP, stored_otp: '+str(stored_otp)})
    
    refund_details = session.get('refund_details')
    refund_number = session.get('refund_mobile')
    
    # Clear refund session data
    session.pop('refund_details', None)
    session.pop('refund_otp', None)
    session.pop('refund_mobile', None)
    
    return jsonify({
        'status': 'success',
        'message': f'Refund of {refund_details["amount"]} TK will be sent to {refund_number} via {refund_details["payment_method"]}. Amount will be credited within 3-5 business days.',
        'redirect': url_for('dashboard')
    })

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Add this function to release expired seats
def release_expired_seat(user_id, booking_details):
    with app.app_context():
        cursor = mysql.connection.cursor()
        try:
            # Check if the seat is still in pending state
            if session.get('booking_details') == booking_details:
                # Clear the booking details
                session.pop('booking_details', None)
                session.pop('otp', None)
                print(f"Released expired seat {booking_details['seat_number']} for user {user_id}")
        except Exception as e:
            print(f"Error releasing seat: {e}")
        finally:
            cursor.close()
@app.route('/payment_verification', methods=['POST'])
def payment_verification():
    if 'user_id' not in session or 'pending_booking' not in session:
        return jsonify({'status': 'error', 'message': 'Session expired'})
    
    payment_method = request.form.get('payment_method')
    session['payment_method'] = payment_method
    
    return jsonify({
        'status': 'success',
        'html': render_template('payment_mobile_popup.html', payment_method=payment_method)
    })

@app.route('/verify_payment_mobile', methods=['POST'])
def verify_payment_mobile():
    mobile = request.form.get('mobile')
    payment_method = session.get('payment_method')
    
    # Store the mobile number in session
    session['payment_mobile'] = mobile
    
    # Generate OTP
    otp = generate_otp()
    session['payment_otp'] = otp
    
    return jsonify({
        'status': 'success',
        'message': f'OTP sent to {mobile}',
        'demo_otp': otp,  # Keep this for demonstration
        'html': render_template('payment_otp_popup.html', payment_method=payment_method)
    })

@app.route('/verify_payment_otp', methods=['POST'])
def verify_payment_otp():
    entered_otp = request.form.get('otp')
    stored_otp = session.get('payment_otp')
    payment_method = session.get('payment_method')
    
    try:
        if entered_otp == stored_otp:
            return jsonify({
                'status': 'success',
                'html': render_template('payment_password_popup.html', payment_method=payment_method)
            })
        return jsonify({'status': 'error', 'message': 'Invalid OTP'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

class TicketPDF(FPDF):
    def header(self):
        try:
            # Try to add logo if it exists
            logo_path = os.path.join('static', 'images', 'logo.png')
            if os.path.exists(logo_path):
                self.image(logo_path, 10, 8, 33)
        except Exception as e:
            print(f"Could not load logo: {e}")
            
        # Add title even if logo fails
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, 'University Transport System', 0, 1, 'C')
        self.ln(20)

def generate_ticket_pdf(user_details, booking_details, route_details):
    pdf = TicketPDF()
    pdf.add_page()
    
    # Set font
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Travel Ticket', 0, 1, 'C')
    pdf.ln(10)
    
    # Add QR Code or Ticket Number
    pdf.set_font('Arial', 'B', 10)
    ticket_number = f"T{user_details['student_id']}{booking_details['journey_date'].strftime('%Y%m%d')}"
    pdf.cell(0, 10, f'Ticket #: {ticket_number}', 0, 1, 'R')
    pdf.ln(5)
    
    # User Details
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Passenger Details:', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Name: {user_details['name']}", 0, 1)
    pdf.cell(0, 10, f"Student ID: {user_details['student_id']}", 0, 1)
    pdf.cell(0, 10, f"Department: {user_details['department']}", 0, 1)
    
    # Journey Details
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Journey Details:', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Route: {route_details['route_name']}", 0, 1)
    pdf.cell(0, 10, f"Stop: {route_details['stop_name']}", 0, 1)
    pdf.cell(0, 10, f"Journey Type: {booking_details['journey_type']}", 0, 1)
    pdf.cell(0, 10, f"Date: {booking_details['journey_date'].strftime('%Y-%m-%d')}", 0, 1)
    pdf.cell(0, 10, f"Shift: {booking_details['shift']}", 0, 1)
    pdf.cell(0, 10, f"Seat Number: {booking_details['seat_number']}", 0, 1)
    
    # Footer
    pdf.ln(20)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 10, 'This is a computer generated ticket and does not require signature.', 0, 1, 'C')
    
    # Generate unique filename
    filename = f"ticket_{user_details['student_id']}_{booking_details['journey_date'].strftime('%Y%m%d')}_{booking_details['seat_number']}.pdf"
    
    # Ensure tickets directory exists
    tickets_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'tickets')
    os.makedirs(tickets_dir, exist_ok=True)
    
    # Save PDF
    filepath = os.path.join(tickets_dir, filename)
    pdf.output(filepath)
    return filename

    

# Run the Flask application with debug mode enabled
if __name__ == '__main__':
    app.run(debug=True)
