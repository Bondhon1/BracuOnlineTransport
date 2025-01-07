import datetime
from flask import Flask, render_template, redirect, url_for, session, flash, request
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




def generate_otp():
    return str(random.randint(100000, 999999))

def send_email(to, subject, body):
    try:
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_USERNAME'],
            recipients=[to],
            body=body
        )
        mail.send(msg)
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")


def send_otp_email(email, otp):
    try:
        msg = Message("Email Verification OTP", 
                      sender=app.config['MAIL_USERNAME'], 
                      recipients=[email])
        msg.body = f"Your OTP for email verification is: {otp}"
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send OTP: {e}")
        return False


@app.route('/')
def index():
    return render_template('index.html')




@app.route('/select_route', methods=['GET', 'POST'])
def select_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()

    # Fetch available routes
    cursor.execute("SELECT route_id, route_name FROM bus_routes")
    routes = cursor.fetchall()

    # Prepare stop_data
    cursor.execute("""
        SELECT route_id, stop_id, stop_name, stop_type
        FROM route_stops
    """)
    stops = cursor.fetchall()
    stop_data = {}
    for stop in stops:
        route_id_key = stop[0]
        if route_id_key not in stop_data:
            stop_data[route_id_key] = []
        stop_data[route_id_key].append({
            'stop_id': stop[1],
            'stop_name': stop[2],
            'stop_type': stop[3]
        })

    cursor.close()
    return render_template('select_route.html', routes=routes, stop_data=stop_data)

@app.route('/select_seat', methods=['GET', 'POST'])
def select_seat():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    route_id = request.args.get('route_id')
    journey_type = request.args.get('journey_type')
    stop_id = request.args.get('stop_id')
    journey_date = date.today()

    if not route_id or not journey_type or not stop_id:
        
        return redirect(url_for('select_route'))

    # Ensure route_id and stop_id are integers
    try:
        route_id = int(route_id) if route_id else None
        stop_id = int(stop_id) if stop_id else None
    except ValueError:
        flash("Invalid route or stop selected. Please try again.", "danger")
        return redirect(url_for('select_route'))

    cursor = mysql.connection.cursor()

    # Check if user already has a booking for this journey type and date
    cursor.execute("""
        SELECT seat_number
        FROM seat_bookings
        WHERE user_id = %s AND journey_type = %s AND journey_date = CURDATE()
    """, (user_id, journey_type))
    existing_booking = cursor.fetchone()
    print("Existing Booking Query Result:", existing_booking)

    if existing_booking:
        flash(f"You already have a {journey_type} booking for today. Please choose another type journey.", "danger")
        return redirect(url_for('dashboard'))

    # Fetch user gender
    cursor.execute("SELECT gender FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    if result:
        user_gender = result[0]
    else:
        flash("Unable to fetch user details. Please contact admin.", "danger")
        return redirect(url_for('select_route'))

    # Fetch stop details
    cursor.execute("""
        SELECT seat_numbers, male_seats, female_seats
        FROM route_stops
        WHERE stop_id = %s
    """, (stop_id,))
    stop_details = cursor.fetchone()

    if not stop_details:
        
        return redirect(url_for('select_route'))

    seat_numbers = stop_details[0].split(',')
    male_seats = stop_details[1].split(',') if stop_details[1] else []
    female_seats = stop_details[2].split(',') if stop_details[2] else []

    # Fetch reserved seats
    cursor.execute("""
        SELECT seat_number
        FROM seat_bookings
        WHERE route_id = %s AND stop_id = %s AND journey_date = CURDATE()
    """, (route_id, stop_id))
    reserved_seats = [row[0] for row in cursor.fetchall()]
    print("Reserved Seats Query Result:", reserved_seats)

    cursor.close()

    return render_template(
        'select_seat.html',
        route_id=route_id,
        journey_type=journey_type,
        stop_id=stop_id,
        seat_numbers=seat_numbers,
        male_seats=male_seats,
        female_seats=female_seats,
        reserved_seats=reserved_seats,
        user_gender=user_gender
    )


@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    route_id = request.form.get('route_id')
    journey_type = request.form.get('journey_type')
    stop_id = request.form.get('stop_id')
    seat_number = request.form.get('seat_number')
    journey_date = date.today()

    if not route_id or not journey_type or not stop_id or not seat_number:
        
        return redirect(url_for('select_route'))

    cursor = mysql.connection.cursor()

    # Check if user already has a booking for this journey type and date
    cursor.execute("""
        SELECT seat_number
        FROM seat_bookings
        WHERE user_id = %s AND journey_type = %s AND journey_date = %s
    """, (user_id, journey_type, journey_date))
    existing_booking = cursor.fetchone()

    if existing_booking:
        flash(f"You already have a {journey_type} booking for today. Please choose a dropoff journey.", "danger")
        return redirect(url_for('select_route'))

    # Insert the booking
    cursor.execute("""
        INSERT INTO seat_bookings (user_id, route_id, stop_id, seat_number, journey_type, journey_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, route_id, stop_id, seat_number, journey_type, journey_date))
    mysql.connection.commit()
    cursor.close()

    flash("Booking confirmed successfully!", "success")
    return redirect(url_for('dashboard'))

@app.route('/send_otp', methods=['POST'])
def send_otp():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    route_id = request.form.get('route_id')
    journey_type = request.form.get('journey_type')
    stop_id = request.form.get('stop_id')
    seat_number = request.form.get('seat_number')
    journey_date = date.today()

    if not route_id or not journey_type or not stop_id or not seat_number:
        flash("Incomplete booking details. Please try again.", "danger")
        return redirect(url_for('select_seat', route_id=route_id, journey_type=journey_type, stop_id=stop_id))

    cursor = mysql.connection.cursor()

    # Re-check if the seat is still available
    cursor.execute("""
        SELECT seat_number
        FROM seat_bookings
        WHERE route_id = %s AND stop_id = %s AND seat_number = %s AND journey_date = %s
    """, (route_id, stop_id, seat_number, journey_date))
    if cursor.fetchone():
        flash("The selected seat has already been booked. Please choose another seat.", "danger")
        return redirect(url_for('select_seat', route_id=route_id, journey_type=journey_type, stop_id=stop_id))

    # Generate OTP and store temporarily
    otp = generate_otp()
    session['otp'] = otp
    session['booking_details'] = {
        'route_id': route_id,
        'journey_type': journey_type,
        'stop_id': stop_id,
        'seat_number': seat_number,
        'journey_date': journey_date,
    }
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()

    if result:
        user_email = result[0]
        print("User Email:", user_email)
        print("Generated OTP:", otp)

        # Send email (using Flask-Mail or smtplib)
        try:
            msg = Message(
                subject="Your OTP for Seat Booking",
                sender=app.config['MAIL_USERNAME'],
                recipients=[user_email],
                body=f"Your OTP is {otp}. Please use this to confirm your booking."
            )
            mail.send(msg)
            
        except Exception as e:
            print("Error sending OTP:", e)
            flash("Failed to send OTP. Please try again later.", "danger")
    else:
        flash("User email not found. Please contact support.", "danger")


    cursor.close()
    return redirect(url_for('confirm_otp', message="OTP has been sent to your inbox.")) 

@app.route('/confirm_otp', methods=['GET', 'POST'])
def confirm_otp():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_otp = request.form.get('otp')
        session_otp = session.get('otp')
        booking_details = session.get('booking_details')
        
        if not booking_details or str(user_otp) != str(session_otp):
            flash("Invalid or expired OTP. Please try again.", "danger")
            return redirect(url_for('select_seat', route_id=booking_details['route_id'], 
                                    journey_type=booking_details['journey_type'], stop_id=booking_details['stop_id'], journey_date=booking_details['journey_date']))

        cursor = mysql.connection.cursor()

        # Final check for seat availability
        cursor.execute("""
            SELECT seat_number
            FROM seat_bookings
            WHERE route_id = %s AND stop_id = %s AND seat_number = %s AND journey_date = %s
        """, (booking_details['route_id'], booking_details['stop_id'], booking_details['seat_number'], booking_details['journey_date']))
        if cursor.fetchone():
            flash("The selected seat has already been booked by another user. Please choose a different seat.", "danger")
            return redirect(url_for('select_seat', route_id=booking_details['route_id'], 
                                    journey_type=booking_details['journey_type'], stop_id=booking_details['stop_id']))

        # Confirm booking
        
        cursor.execute("""
            INSERT INTO seat_bookings (user_id, route_id, stop_id, seat_number, journey_type, journey_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session['user_id'], booking_details['route_id'], booking_details['stop_id'], 
              booking_details['seat_number'], booking_details['journey_type'], date.today()))
        mysql.connection.commit()
        cursor.close()

        # Clear session data
        session.pop('otp', None)
        session.pop('booking_details', None)

        flash("Booking confirmed successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('confirm_otp.html')


@app.route('/add_bus_route', methods=['GET', 'POST'])
def add_bus_route():
    if 'admin_id' not in session:
        return redirect(url_for('adminlogin'))

    form = AddBusRouteForm()
    if form.validate_on_submit():
        route_name = form.route_name.data
        bus_number = form.bus_number.data
        driver_name = form.driver_name.data
        capacity = form.capacity.data

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO bus_routes (route_name, bus_number, driver_name, capacity)
            VALUES (%s, %s, %s, %s)
        """, (route_name, bus_number, driver_name, capacity))
        mysql.connection.commit()
        cursor.close()

        flash("Bus route added successfully!", "success")
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_bus_route.html', form=form)

# Route for adding bus stops
@app.route('/add_bus_stop', methods=['GET', 'POST'])
def add_bus_stop():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        bus_id = request.form['bus_id']
        stop_name = request.form['stop_name']
        stop_type = request.form['stop_type']
        time = request.form['time']
        fare = request.form['fare']
        seat_numbers = request.form['seat_numbers']
        male_reserved_seats = request.form.get('male_reserved_seats', "")
        female_reserved_seats = request.form.get('female_reserved_seats', "")

        # Normalize seat data
        all_seats = seat_numbers.split(',')
        male_seats = male_reserved_seats.split(',')
        female_seats = female_reserved_seats.split(',')

        # Check for conflicts
        conflicting_seats = set(male_seats) & set(female_seats)
        if conflicting_seats:
            flash(f"Conflict in reserved seats: {', '.join(conflicting_seats)}", "danger")
            return redirect(url_for('add_bus_stop'))

        # Insert data into the database
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO route_stops (route_id, stop_name, stop_type, pickup_time, dropoff_time, fare, seat_numbers, male_seats, female_seats)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            bus_id,
            stop_name,
            stop_type,
            time if stop_type == 'pickup' else None,
            time if stop_type == 'dropoff' else None,
            fare,
            ",".join(all_seats),
            ",".join(male_seats),
            ",".join(female_seats)
        ))
        mysql.connection.commit()
        cursor.close()

        flash('Bus stop added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    # Fetch bus routes
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT route_id, route_name FROM bus_routes")
    buses = cursor.fetchall()
    cursor.close()

    return render_template('add_bus_stop.html', buses=buses)




@app.route('/logout')
def logout():
    # Determine the current session type
    if 'user_id' in session:
        session.pop('user_id', None)
        flash("You have been logged out successfully.")
        return redirect(url_for('login'))

    elif 'staff_id' in session:
        session.pop('staff_id', None)
        flash("You have been logged out successfully.")
        return redirect(url_for('staff_login'))

    elif 'admin_id' in session:
        session.pop('admin_id', None)
        flash("Admin has been logged out successfully.")
        return redirect(url_for('adminlogin'))

    # Default case if no session exists
    flash("You are not logged in.")
    return redirect(url_for('index'))


# Run the Flask application with debug mode enabled
if __name__ == '__main__':
    app.run(debug=True)
