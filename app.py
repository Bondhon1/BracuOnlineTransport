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
        
class AddAdminForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])  
    email = StringField("Email", validators=[DataRequired(), Email()])  
    password = PasswordField("Password", validators=[DataRequired()])  
    submit = SubmitField("Add Admin") 

# Form for adding a bus stop
class AddBusStopForm(FlaskForm):
    route_id = SelectField("Route", coerce=int, validators=[DataRequired()])
    stop_name = StringField("Stop Name", validators=[DataRequired()])
    pickup_time = TimeField("Pickup Time", validators=[DataRequired()])
    dropoff_time = TimeField("Drop-off Time", validators=[DataRequired()])
    fare = FloatField("Fare", validators=[DataRequired()])
    stop_type = SelectField("Stop Type", choices=[("Pickup", "Pickup"), ("Drop-off", "Drop-off")], validators=[DataRequired()])
    submit = SubmitField("Add Stop")

class AddBusRouteForm(FlaskForm):
    route_name = StringField("Route Name", validators=[DataRequired()])
    bus_number = StringField("Bus Number", validators=[DataRequired()])
    driver_name = StringField("Driver Name")
    capacity = IntegerField("Capacity", validators=[DataRequired()])
    submit = SubmitField("Add Route")


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


@app.route('/add_admin', methods=['GET', 'POST'])
def add_admin():
    if 'admin_id' not in session:
        return redirect(url_for('adminlogin'))

    form = AddAdminForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO admins (name, email, password) VALUES (%s, %s, %s)",
                       (username, email, password))
        mysql.connection.commit()
        cursor.close()

        flash('New admin added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_admin.html', form=form)
@app.route('/admin/add_offdays', methods=['GET', 'POST'])
def add_offdays():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        off_dates = request.form.getlist('off_dates[]')  # List of off-days
        description = request.form.get('description', None)

        cursor = mysql.connection.cursor()
        for off_date in off_dates:
            cursor.execute("""
                INSERT INTO bus_offdays (off_date, description)
                VALUES (%s, %s)
            """, (off_date, description))
        mysql.connection.commit()
        cursor.close()

        flash('Off-days added successfully!', 'success')
        return redirect(url_for('view_offdays'))

    return render_template('add_offdays.html')


@app.route('/admin/view_offdays', methods=['GET', 'POST'])
def view_offdays():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, off_date, description, created_at FROM bus_offdays ORDER BY off_date ASC")
    offdays = cursor.fetchall()
    cursor.close()

    return render_template('view_offdays.html', offdays=offdays)


@app.route('/admin/delete_offday/<int:offday_id>', methods=['POST'])
def delete_offday(offday_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM bus_offdays WHERE id = %s", (offday_id,))
    mysql.connection.commit()
    cursor.close()

    flash('Off-day deleted successfully!', 'success')
    return redirect(url_for('view_offdays'))


@app.route('/select_route', methods=['GET', 'POST'])
def select_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    # Check for off days
    current_date = datetime.now().date()
    current_day = datetime.now().strftime('%A')

    # Check if today is a weekend or in the bus_offdays table
    if current_day in ['Saturday', 'Sunday']:
        flash("Today is an off day. Ticket booking is not allowed.", "danger")
        return redirect(url_for('dashboard'))

    cursor.execute("SELECT off_date FROM bus_offdays WHERE off_date = %s", (current_date,))
    off_day = cursor.fetchone()

    if off_day:
        flash("Ticket booking is not allowed on scheduled off days.", "danger")
        return redirect(url_for('dashboard'))

    # Check if the user has already booked a pickup or dropoff journey
    cursor.execute("""
        SELECT journey_type
        FROM seat_bookings
        WHERE user_id = %s AND journey_date = CURDATE()
    """, (user_id,))
    existing_booking = cursor.fetchall()

    # Determine allowed journey type based on existing booking
    allowed_journey_type = "pickup/dropoff"
    if existing_booking:
        if len(existing_booking) == 2:
            allowed_journey_type = "No_option"
        elif existing_booking[0][0] == "pickup":
            allowed_journey_type = "dropoff"
        elif existing_booking[0][0] == "dropoff":
            allowed_journey_type = "pickup"

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

    return render_template(
        'select_route.html',
        routes=routes,
        stop_data=stop_data,
        allowed_journey_type=allowed_journey_type
    )


@app.route('/select_seat', methods=['GET', 'POST'])
def select_seat():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    route_id = request.args.get('route_id')
    journey_type = request.args.get('journey_type')
    stop_id = request.args.get('stop_id')
    shift = request.args.get('shift')  # Added shift
    journey_date = date.today()

    if not route_id or not journey_type or not stop_id or not shift:
        return redirect(url_for('select_route'))

    try:
        route_id = int(route_id)
        stop_id = int(stop_id)
        shift = int(shift)
    except ValueError:
        flash("Invalid data provided. Please try again.", "danger")
        return redirect(url_for('select_route'))

    cursor = mysql.connection.cursor()

    # Fetch user details
    cursor.execute("""
        SELECT name, email, student_id, department, gender
        FROM users
        WHERE id = %s
    """, (user_id,))
    user_details = cursor.fetchone()
    if not user_details:
        flash("Unable to fetch user details. Please contact admin.", "danger")
        return redirect(url_for('dashboard'))

    user_info = {
        'name': user_details[0],
        'email': user_details[1],
        'student_id': user_details[2],
        'department': user_details[3],
        'gender': user_details[4]
    }

    # Fetch seat capacity
    cursor.execute("SELECT capacity FROM bus_routes WHERE route_id = %s", (route_id,))
    capacity = cursor.fetchone()
    capacity = capacity[0] if capacity else 40

    rows = capacity // 4
    all_seat_numbers = [f"{chr(65 + i)}{j+1}" for i in range(rows) for j in range(4)]

    # Fetch stop details
    cursor.execute("""
        SELECT seat_numbers, male_seats, female_seats
        FROM route_stops
        WHERE stop_id = %s
    """, (stop_id,))
    stop_details = cursor.fetchone()

    if not stop_details:
        flash("Invalid stop details. Please try again.", "danger")
        return redirect(url_for('select_route'))

    available_seats = stop_details[0].split(',') if stop_details[0] else []
    male_seats = stop_details[1].split(',') if stop_details[1] else []
    female_seats = stop_details[2].split(',') if stop_details[2] else []

    reserved_other_routes = list(set(all_seat_numbers) - set(available_seats))

    # Fetch reserved seats for the chosen stop, journey type, and shift
    cursor.execute("""
        SELECT seat_number
        FROM seat_bookings
        WHERE route_id = %s AND stop_id = %s AND journey_date = CURDATE() AND shift = %s
    """, (route_id, stop_id, shift))
    reserved_seats = [row[0] for row in cursor.fetchall()]

    cursor.close()

    return render_template(
        'select_seat.html',
        route_id=route_id,
        journey_type=journey_type,
        stop_id=stop_id,
        shift=shift,
        seat_numbers=all_seat_numbers,
        male_seats=male_seats,
        female_seats=female_seats,
        reserved_seats=reserved_seats,
        reserved_other_routes=reserved_other_routes,
        user_info=user_info,
        user_gender=user_info['gender'],
        timer_duration=60
    )


@app.route('/send_otp', methods=['POST'])
def send_otp():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    route_id = request.form.get('route_id')
    journey_type = request.form.get('journey_type')
    stop_id = request.form.get('stop_id')
    seat_number = request.form.get('seat_number')
    shift = request.form.get('shift')  # Capture the shift value
    journey_date = date.today()

    if not route_id or not journey_type or not stop_id or not seat_number or not shift:
        flash("Incomplete booking details. Please try again.", "danger")
        return redirect(url_for('select_seat', route_id=route_id, journey_type=journey_type, stop_id=stop_id, shift=shift))

    # Re-check if the seat is still available
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT seat_number
        FROM seat_bookings
        WHERE route_id = %s AND stop_id = %s AND seat_number = %s AND journey_date = %s AND shift = %s
    """, (route_id, stop_id, seat_number, journey_date, shift))
    already_reserved = cursor.fetchone()
    if already_reserved:
        flash("The selected seat has already been booked. Please choose another seat.", "danger")
        return redirect(url_for('select_seat', route_id=route_id, journey_type=journey_type, stop_id=stop_id, shift=shift))

    # Generate OTP and store details
    otp = generate_otp()
    session['otp'] = otp
    session['booking_details'] = {
        'route_id': route_id,
        'journey_type': journey_type,
        'stop_id': stop_id,
        'seat_number': seat_number,
        'shift': shift,  # Add shift to booking_details
        'journey_date': journey_date,
    }

    cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()

    if result:
        user_email = result[0]
        print("User Email:", user_email)
        print("Generated OTP:", otp)

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
                                    journey_type=booking_details['journey_type'], stop_id=booking_details['stop_id'], shift=booking_details['shift']))

        # Check for seat availability (same logic as before)
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT seat_number
            FROM seat_bookings
            WHERE route_id = %s AND stop_id = %s AND seat_number = %s AND journey_date = %s AND shift = %s
        """, (booking_details['route_id'], booking_details['stop_id'], booking_details['seat_number'], date.today(), booking_details['shift']))
        already_reserved = cursor.fetchone()
        if already_reserved:
            flash("The selected seat has already been booked by another user. Please choose a different seat.", "danger")
            return redirect(url_for('select_seat', route_id=booking_details['route_id'],
                                    journey_type=booking_details['journey_type'], stop_id=booking_details['stop_id'], shift=booking_details['shift']))

        # Set session flag for redirection to payment
        session['redirect_to_payment'] = True
        session['pending_booking'] = booking_details

        # Clear OTP data
        session.pop('otp', None)

       
        return render_template('confirm_otp.html', redirect_to_payment=True)

    return render_template('confirm_otp.html', redirect_to_payment=False)

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
        times = request.form.getlist('times[]')  # Retrieve all entered times
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

        cursor = mysql.connection.cursor()

        # Insert stop into route_stops table
        cursor.execute("""
            INSERT INTO route_stops (route_id, stop_name, stop_type, fare, seat_numbers, male_seats, female_seats)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            bus_id,
            stop_name,
            stop_type,
            fare,
            ",".join(all_seats),
            ",".join(male_seats),
            ",".join(female_seats)
        ))
        stop_id = cursor.lastrowid  # Get the last inserted stop_id

        # Insert times into trip_times table with the correct shift value
        for index, trip_time in enumerate(times):
            shift = index + 1  # Assign shift 1 for the first time, and shift 2 for the second
            cursor.execute("""
                INSERT INTO trip_times (stop_id, trip_time, shift)
                VALUES (%s, %s, %s)
            """, (stop_id, trip_time, shift))

        mysql.connection.commit()
        cursor.close()

        flash('Bus stop added successfully with multiple trips!', 'success')
        return redirect(url_for('admin_dashboard'))

    # Fetch bus routes
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT route_id, route_name FROM bus_routes")
    buses = cursor.fetchall()
    cursor.close()

    return render_template('add_bus_stop.html', buses=buses)


@app.route('/view_schedules')
def view_schedules():
    cursor = mysql.connection.cursor()

    # Fetch all bus routes
    cursor.execute("""
        SELECT route_id, route_name, bus_number, driver_name
        FROM bus_routes
    """)
    bus_routes = cursor.fetchall()

    # Fetch stops and times for each route, organized by shift and type
    cursor.execute("""
        SELECT rs.route_id, rs.stop_name, tt.trip_time, rs.stop_type, tt.shift
        FROM route_stops rs
        LEFT JOIN trip_times tt ON rs.stop_id = tt.stop_id
        ORDER BY rs.route_id, rs.stop_type, tt.shift, tt.trip_time
    """)
    stops_and_times = cursor.fetchall()
    cursor.close()

    # Organize data
    schedules = {}
    for route in bus_routes:
        route_id = route[0]
        if route_id not in schedules:
            schedules[route_id] = {
                "route_name": route[1],
                "bus_number": route[2],
                "driver_name": route[3],
                "pickup": {"shift1": [], "shift2": []},
                "dropoff": {"shift1": [], "shift2": []}
            }

    for stop in stops_and_times:
        route_id = stop[0]
        if route_id in schedules:
            stop_info = {
                "stop_name": stop[1],
                "time": stop[2] if stop[2] else "N/A"
            }
            if stop[3] == "pickup":
                schedules[route_id]["pickup"][f"shift{stop[4]}"].append(stop_info)
            elif stop[3] == "dropoff":
                schedules[route_id]["dropoff"][f"shift{stop[4]}"].append(stop_info)

    return render_template('view_schedules.html', schedules=schedules)

# Route for adding bus stops
@app.route('/add_bus_stop', methods=['GET', 'POST'])
def add_bus_stop():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        bus_id = request.form['bus_id']
        stop_name = request.form['stop_name']
        stop_type = request.form['stop_type']
        times = request.form.getlist('times[]')  # Retrieve all entered times
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

        cursor = mysql.connection.cursor()

        # Insert stop into route_stops table
        cursor.execute("""
            INSERT INTO route_stops (route_id, stop_name, stop_type, fare, seat_numbers, male_seats, female_seats)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            bus_id,
            stop_name,
            stop_type,
            fare,
            ",".join(all_seats),
            ",".join(male_seats),
            ",".join(female_seats)
        ))
        stop_id = cursor.lastrowid  # Get the last inserted stop_id

        # Insert times into trip_times table with the correct shift value
        for index, trip_time in enumerate(times):
            shift = index + 1  # Assign shift 1 for the first time, and shift 2 for the second
            cursor.execute("""
                INSERT INTO trip_times (stop_id, trip_time, shift)
                VALUES (%s, %s, %s)
            """, (stop_id, trip_time, shift))

        mysql.connection.commit()
        cursor.close()

        flash('Bus stop added successfully with multiple trips!', 'success')
        return redirect(url_for('admin_dashboard'))

    # Fetch bus routes
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT route_id, route_name FROM bus_routes")
    buses = cursor.fetchall()
    cursor.close()

    return render_template('add_bus_stop.html', buses=buses)


# Run the Flask application with debug mode enabled
if __name__ == '__main__':
    app.run(debug=True)
