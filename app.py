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


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()]) 
    email = StringField("Email", validators=[DataRequired(), Email()]) 
    password = PasswordField("Password", validators=[DataRequired()])  
    submit = SubmitField("Register")  

    
    def validate_email(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (field.data,))  
        user = cursor.fetchone()  
        cursor.close()  
        if user:
            raise ValidationError('Email Already Taken')

class StaffRegisterForm(FlaskForm):
    initial = StringField("Initial", validators=[DataRequired()]) 
    email = StringField("Email", validators=[DataRequired(), Email()]) 
    password = PasswordField("Password", validators=[DataRequired()])  
    submit = SubmitField("Register")  

    
    def validate_email(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (field.data,))  
        user = cursor.fetchone()  
        cursor.close()  
        if user:
            raise ValidationError('Email Already Taken')
        

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()]) 
    password = PasswordField("Password", validators=[DataRequired()])  
    submit = SubmitField("Login")

class AdminLoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()]) 
    password = PasswordField("Password", validators=[DataRequired()])  
    submit = SubmitField("Login")  

class StaffLoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()]) 
    password = PasswordField("Password", validators=[DataRequired()])  
    submit = SubmitField("Login")

class AddAdminForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])  
    email = StringField("Email", validators=[DataRequired(), Email()])  
    password = PasswordField("Password", validators=[DataRequired()])  
    submit = SubmitField("Add Admin") 



class UpdateProfileForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=50)])
    student_id = IntegerField("Student ID", validators=[DataRequired()])
    department = SelectField("Department", choices=[('CSE', 'CSE'), ('EEE', 'EEE'), ('ANT', 'ANT'), ('BBA', 'BBA'), ('PHY', 'PHY')], validators=[DataRequired()])
    gender = SelectField("Gender", choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired(), Length(max=100)])
    mobile_number = IntegerField("Mobile Number", validators=[DataRequired()])
    blood_group = StringField("Blood Group", validators=[DataRequired(), Length(max=3)])
    profile_image = FileField("Profile Image", validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField("Update Profile")

    def validate_student_id(form, field):
        if len(str(field.data)) != 8:
            raise ValidationError('Student ID must be exactly 8 digits long.')



class StaffUpdateProfileForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=50)])
    PIN = IntegerField("PIN", validators=[DataRequired()])
    department = SelectField("Department", choices=[('CSE', 'CSE'), ('EEE', 'EEE'), ('ANT', 'ANT'), ('BBA', 'BBA'), ('PHY', 'PHY')], validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired(), Length(max=100)])
    mobile_number = IntegerField("Mobile Number", validators=[DataRequired()])
    blood_group = StringField("Blood Group", validators=[DataRequired(), Length(max=3)])
    profile_image = FileField("Profile Image", validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField("Update Profile")

    def validate_PIN(form, field):
        if len(str(field.data)) != 5:
            raise ValidationError('PIN must be exactly 5 digits long.')
        

class AddScheduleForm(FlaskForm):
    route_name = StringField("Route Name", validators=[DataRequired()])
    departure_time = TimeField("Departure Time", format='%H:%M', validators=[DataRequired()])
    arrival_time = TimeField("Arrival Time", format='%H:%M', validators=[DataRequired()])
    bus_number = StringField("Bus Number", validators=[DataRequired()])
    driver_name = StringField("Driver Name")
    capacity = IntegerField("Capacity")
    submit = SubmitField("Add Schedule")

class AddBusRouteForm(FlaskForm):
    route_name = StringField("Route Name", validators=[DataRequired()])
    bus_number = StringField("Bus Number", validators=[DataRequired()])
    driver_name = StringField("Driver Name")
    capacity = IntegerField("Capacity", validators=[DataRequired()])
    submit = SubmitField("Add Route")

# Feedback form class using Flask-WTF and WTForms
class FeedbackForm(FlaskForm):
    bus_number = StringField('Bus Number', validators=[DataRequired()])
    feedback = TextAreaField('Feedback', validators=[DataRequired(), Length(min=10, max=500)])
    rating = IntegerField('Rating (1-5)', validators=[DataRequired()])
    journey_date = DateField('Journey Date', validators=[DataRequired()])
    submit = SubmitField('Submit Feedback')


# Form for adding a bus stop
class AddBusStopForm(FlaskForm):
    route_id = SelectField("Route", coerce=int, validators=[DataRequired()])
    stop_name = StringField("Stop Name", validators=[DataRequired()])
    pickup_time = TimeField("Pickup Time", validators=[DataRequired()])
    dropoff_time = TimeField("Drop-off Time", validators=[DataRequired()])
    fare = FloatField("Fare", validators=[DataRequired()])
    stop_type = SelectField("Stop Type", choices=[("Pickup", "Pickup"), ("Drop-off", "Drop-off")], validators=[DataRequired()])
    submit = SubmitField("Add Stop")

class VehicleRequestForm(FlaskForm):
    journey_date = DateField("Journey Date", format='%Y-%m-%d', validators=[DataRequired(), future_date])
    pickup_time = TimeField("Pickup Time", format='%H:%M', validators=[DataRequired()])
    pickup_location = StringField("Pickup Location", validators=[DataRequired(), Length(max=100)])
    destination = StringField("Destination", validators=[DataRequired(), Length(max=100)])
    capacity = IntegerField("Capacity", validators=[DataRequired(), NumberRange(min=1, message="Capacity must be at least 1")])
    submit = SubmitField("Submit Request")

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()  
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
        
        otp = generate_otp()
        session['otp'] = otp
        session['email'] = email
        session['name'] = name
        session['password'] = password
        
        if send_otp_email(email, otp):
            return redirect(url_for('verify_email', message="OTP has been sent to your inbox"))
        else:
            flash("Failed to send OTP. Try again.", "danger")
            
    return render_template('register.html', form=form)

@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    message = request.args.get('message', None)  # Fetch message from the query string
    
    if request.method == 'POST':
        entered_otp = request.form['otp']
        if entered_otp == session.get('otp'):
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, password, verified) 
                VALUES (%s, %s, %s, %s)
            """, (session['name'], session['email'], session['password'], True))
            mysql.connection.commit()
            cursor.close()
            
            flash("Registration successful! You can log in now.", "success")
            session.pop('otp', None)
            session.pop('email', None)
            session.pop('name', None)
            session.pop('password', None)
            return redirect(url_for('login'))
        else:
             return redirect(url_for('verify_email', message="Invalid OTP. Please try again."))
    
    return render_template('verify_email.html', message=message)

@app.route('/staff_register', methods=['GET', 'POST'])
def staff_register():
    form = StaffRegisterForm()

    if form.validate_on_submit():
        initial = form.initial.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Generate OTP and store it in session
        otp = str(random.randint(100000, 999999))
        session['staff_initial'] = initial
        session['staff_email'] = email
        session['staff_password'] = hashed_password.decode('utf-8')
        session['staff_otp'] = otp

        # Send email and redirect to OTP verification
        try:
            send_email(email, "Email Verification", f"Your OTP is: {otp}")
            return redirect(url_for('verify_staff_email', message="OTP has been sent to your inbox."))
        except Exception as e:
            flash(f"Failed to send OTP. Error: {str(e)}", "danger")
            return redirect(url_for('staff_register'))

    return render_template('staff_register.html', form=form)


@app.route('/verify_staff_email', methods=['GET', 'POST'])
def verify_staff_email():
    message = request.args.get('message')  # Fetch the message from the query string

    if request.method == 'POST':
        entered_otp = request.form['otp']

        if entered_otp == session.get('staff_otp'):
            # Store the staff in the database
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO staffs (initial, email, password, verified) 
                VALUES (%s, %s, %s, %s)
            """, (session['staff_initial'], session['staff_email'], session['staff_password'], True))
            mysql.connection.commit()
            cursor.close()

            # Clear session data after successful registration
            session.pop('staff_otp', None)
            session.pop('staff_email', None)
            session.pop('staff_initial', None)
            session.pop('staff_password', None)
            flash("Registration successful! You can log in now.")
            return redirect(url_for('staff_login'))
        else:
            return redirect(url_for('verify_staff_email', message="Invalid OTP. Please try again."))

    return render_template('verify_staff_email.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm() 
    if form.validate_on_submit():  
        email = form.email.data 
        password = form.password.data  

       
        cursor = mysql.connection.cursor()  # Create a cursor to interact with the database
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))  # Query to find the user by email
        user = cursor.fetchone()  # Fetch one record
        cursor.close()  # Close the cursor

        # Check if the user exists and if the password matches
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]  # Store the user's ID in the session
            return redirect(url_for('dashboard'))  # Redirect to the dashboard
        else:
            flash("Login failed. Please check your email and password")  # Flash an error message
            return redirect(url_for('login'))  # Redirect to the login page

    return render_template('login.html', form=form)  # Render the login page with the form

@app.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
    form = StaffLoginForm() 
    if form.validate_on_submit():  
        email = form.email.data 
        password = form.password.data  

        # Query the correct table 'staffs'
        cursor = mysql.connection.cursor() 
        cursor.execute("SELECT * FROM staffs WHERE email=%s", (email,))  
        staff = cursor.fetchone()  
        cursor.close()  

        # Validate staff credentials
        if staff and bcrypt.checkpw(password.encode('utf-8'), staff[3].encode('utf-8')):
            session['staff_id'] = staff[0]  # Correct session key for staff
            return redirect(url_for('staff_dashboard'))  
        else:
            flash("Login failed. Please check your staff email and password", "danger") 
            return redirect(url_for('staff_login'))  

    return render_template('staff_login.html', form=form)  


# Define the route for Admin login
@app.route('/admin_login', methods=['GET', 'POST'])
def adminlogin():
    form = AdminLoginForm()  # Create an instance of the login form
    if form.validate_on_submit():  # If the form is submitted and valid
        email = form.email.data  # Get the email from the form
        password = form.password.data  # Get the password from the form

        # Query the database to find the admin by email and password
        cursor = mysql.connection.cursor()  # Create a cursor to interact with the database
        cursor.execute("SELECT * FROM admins WHERE email=%s AND password=%s", (email, password))  # Query to find the admin by email and password
        admin = cursor.fetchone()  # Fetch one record
        cursor.close()  # Close the cursor

        if admin:
            session['admin_id'] = admin[0]  # Store the admin's ID in the session
            return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard
        else:
            flash("Login failed. Please check your email and password")  # Flash an error message
            return redirect(url_for('adminlogin'))  # Redirect to the login page

    return render_template('admin_login.html', form=form)  # Render the admin login page with the form

# Define the route for the user dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    # Add today's date for the feedback link
    today = date.today().strftime('%Y-%m-%d')

    # Fetch user details
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    # Fetch user's tickets (current and upcoming journeys)
    cursor.execute("""
        SELECT 
            COALESCE(sb.booking_id, 0) as booking_id,
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
            tt.trip_time
        FROM seat_bookings sb
        JOIN bus_routes br ON sb.route_id = br.route_id
        JOIN route_stops rs ON sb.stop_id = rs.stop_id
        JOIN trip_times tt ON sb.trip_id = tt.trip_id
        WHERE sb.user_id = %s AND sb.journey_date >= CURDATE()
        ORDER BY sb.journey_date ASC
    """, (user_id,))
    tickets = cursor.fetchall()

    # Fetch user's feedbacks and admin replies
    cursor.execute("""
        SELECT feedback, rating, reply, journey_date 
        FROM feedback 
        WHERE user_id=%s 
        ORDER BY journey_date DESC
    """, (user_id,))
    feedbacks = cursor.fetchall()

    # Count unread replies
    cursor.execute("""
        SELECT COUNT(*) 
        FROM feedback 
        WHERE user_id=%s AND reply IS NOT NULL AND viewed=0
    """, (user_id,))
    new_replies_count = cursor.fetchone()[0]

    # Mark all replies as viewed
    cursor.execute("""
        UPDATE feedback 
        SET viewed=1 
        WHERE user_id=%s AND reply IS NOT NULL
    """, (user_id,))
    mysql.connection.commit()

    # Fetch user's past travel history with route and stop names
    cursor.execute("""
        SELECT br.route_name, rs.stop_name, sb.seat_number, sb.journey_type, sb.journey_date 
        FROM seat_bookings sb
        JOIN bus_routes br ON sb.route_id = br.route_id
        JOIN route_stops rs ON sb.stop_id = rs.stop_id
        WHERE sb.user_id = %s AND sb.journey_date < CURDATE()
        ORDER BY sb.journey_date DESC
    """, (user_id,))
    travel_history = cursor.fetchall()

    cursor.close()

    # Fetch and remove the profile update message from the session
    profile_update_message = session.pop('profile_update_message', None)

    return render_template(
        'dashboard.html',
        user=user,
        tickets=tickets,
        feedbacks=feedbacks,
        new_replies_count=new_replies_count,
        profile_update_message=profile_update_message,
        travel_history=travel_history,
        today=today  # Pass today's date to the template
    )

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

@app.route('/add_feedback/<route_name>/<journey_date>', methods=['GET', 'POST'])
def add_feedback(route_name, journey_date):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    cursor = mysql.connection.cursor()

    # Fetch the bus number for the route
    cursor.execute("SELECT bus_number FROM bus_routes WHERE route_name = %s", (route_name,))
    bus_details = cursor.fetchone()
    if not bus_details:
        flash("Unable to fetch bus details for the selected route. Please contact admin.", "danger")
        return redirect(url_for('dashboard'))

    bus_number = bus_details[0]

    if request.method == 'POST':
        rating = request.form.get('rating')
        feedback = request.form.get('feedback')

        # Fetch username and email for the user
        cursor.execute("SELECT name, email FROM users WHERE id = %s", (user_id,))
        user_details = cursor.fetchone()
        if not user_details:
            flash("Unable to fetch user details. Please contact admin.", "danger")
            return redirect(url_for('dashboard'))

        username, email = user_details

        # Insert feedback with username, email, and bus number
        cursor.execute("""
            INSERT INTO feedback (user_id, name, email, route_name, bus_number, journey_date, rating, feedback)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, username, email, route_name, bus_number, journey_date, rating, feedback))
        mysql.connection.commit()
        cursor.close()

        flash("Feedback submitted successfully!", "success")
        return redirect(url_for('dashboard'))

    cursor.close()
    return render_template('add_feedback.html', route_name=route_name, journey_date=journey_date, bus_number=bus_number)


@app.route('/staff_dashboard')
def staff_dashboard():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    staff_id = session['staff_id']

    # Fetch staff details
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM staffs WHERE id=%s", (staff_id,))
    staff = cursor.fetchone()

    # Fetch recent vehicle requests
    cursor.execute("""
        SELECT journey_date, pickup_location, destination, capacity, reply, status
        FROM vehicle_requests
        WHERE staff_id=%s
        ORDER BY journey_date DESC
        LIMIT 5
    """, (staff_id,))
    vehicle_requests = cursor.fetchall()

    # Count unread replies
    cursor.execute("""
        SELECT COUNT(*)
        FROM vehicle_requests
        WHERE staff_id=%s AND reply IS NOT NULL AND viewed=0
    """, (staff_id,))
    new_replies_count = cursor.fetchone()[0]

    # Mark replies as viewed
    cursor.execute("""
        UPDATE vehicle_requests
        SET viewed=1
        WHERE staff_id=%s AND reply IS NOT NULL
    """, (staff_id,))
    mysql.connection.commit()

    cursor.close()

    # Get and remove the vehicle request success message from the session
    vehicle_request_message = session.pop('vehicle_request_message', None)

    return render_template(
        'staff_dashboard.html',
        staff=staff,
        vehicle_requests=vehicle_requests,
        new_replies_count=new_replies_count,
        vehicle_request_message=vehicle_request_message
    )


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' in session:
        admin_id = session['admin_id']

        cursor = mysql.connection.cursor()

        # Fetch admin details
        cursor.execute("SELECT name, email FROM admins WHERE admin_id = %s", (admin_id,))
        admin = cursor.fetchone()

        # Fetch analytics data
        cursor.execute("SELECT (SELECT COUNT(*) FROM users) + (SELECT COUNT(*) FROM staffs)")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vehicle_requests WHERE status = 'Pending'")
        pending_requests = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM feedback WHERE reply IS NULL")
        pending_feedback = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM seat_bookings")
        total_bookings = cursor.fetchone()[0]

        # Fetch insights
        cursor.execute("""
            SELECT route_name, COUNT(*) AS bookings
            FROM seat_bookings sb
            JOIN bus_routes br ON sb.route_id = br.route_id
            GROUP BY br.route_id
            ORDER BY bookings DESC LIMIT 1
        """)
        most_used_route = cursor.fetchone()
        most_used_route = most_used_route[0] if most_used_route else "N/A"

        cursor.execute("""
            SELECT DATE(sb.journey_date), COUNT(*) AS bookings
            FROM seat_bookings sb
            GROUP BY DATE(sb.journey_date)
            ORDER BY bookings DESC LIMIT 1
        """)
        highest_booking_day = cursor.fetchone()
        highest_booking_day = highest_booking_day[0] if highest_booking_day else "N/A"

        cursor.execute("""
            SELECT HOUR(tt.trip_time), COUNT(*) AS bookings
            FROM seat_bookings sb
            JOIN trip_times tt ON sb.trip_id = tt.trip_id
            GROUP BY HOUR(tt.trip_time)
            ORDER BY bookings DESC LIMIT 1
        """)
        peak_travel_time = cursor.fetchone()
        peak_travel_time = f"{peak_travel_time[0]}:00" if peak_travel_time else "N/A"

        cursor.close()

        return render_template(
            'admin_dashboard.html',
            admin=admin,
            total_users=total_users,
            pending_requests=pending_requests,
            pending_feedback=pending_feedback,
            total_bookings=total_bookings,
            most_used_route=most_used_route,
            highest_booking_day=highest_booking_day,
            peak_travel_time=peak_travel_time,
        )
    else:
        return redirect(url_for('adminlogin'))



def send_email_notification(recipient, subject, message):
    try:
        msg = Message(subject, recipients=[recipient])
        msg.body = message
        mail.send(msg)
        print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/admin/view_schedules', methods=['GET', 'POST'])
def view_admin_schedules():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        trip_id = request.form.get('trip_id')
        stop_id = request.form.get('stop_id')  # Get stop_id from the form
        shift = request.form['shift']
        new_time = request.form['new_time']
        print(f"Received stop_id: {stop_id}, trip_id: {trip_id}, shift: {shift}, new_time: {new_time}")

        cursor = mysql.connection.cursor()
        if not trip_id:  # Insert new shift
            cursor.execute("""
                INSERT INTO trip_times (stop_id, trip_time, shift)
                VALUES (%s, %s, %s)
            """, (stop_id, new_time, shift))
            mysql.connection.commit()
            flash(f"Shift {shift} time added successfully!", "success")
        else:  # Update existing shift
            cursor.execute("""
                UPDATE trip_times
                SET trip_time = %s
                WHERE trip_id = %s
            """, (new_time, trip_id))
            mysql.connection.commit()
            flash(f"Shift {shift} time updated successfully!", "success")

            # Notify affected users
            cursor.execute("""
                SELECT id, email, name FROM users
            """)
            affected_users = cursor.fetchall()

            for user in affected_users:
                try:
                    msg = Message(
                        subject="Bus Schedule Update",
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[user[1]],  # User email
                        body=f"Dear {user[2]},\n\nThe schedule for your booked trip has been updated. "
                             f"Please check the updated times on your dashboard.\n\nBest Regards,\nUniversity Transport System"
                    )
                    mail.send(msg)
                    print(f"Email sent to {user[1]}")
                except Exception as e:
                    print(f"Error sending email to {user[1]}: {e}")

        cursor.close()
        return redirect(url_for('view_admin_schedules'))

    # Fetch data for GET request
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT route_id, route_name, bus_number, driver_name
        FROM bus_routes
    """)
    bus_routes = cursor.fetchall()

    cursor.execute("""
        SELECT rs.route_id, rs.stop_id, rs.stop_name, tt.trip_id, tt.trip_time, rs.stop_type, tt.shift
        FROM route_stops rs
        LEFT JOIN trip_times tt ON rs.stop_id = tt.stop_id
        ORDER BY rs.route_id, rs.stop_type, rs.stop_name, tt.shift
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
        route_id, stop_id, stop_name, trip_id, trip_time, stop_type, shift = stop
        stop_info = {
            "stop_id": stop_id,
            "stop_name": stop_name,
            "trip_id": trip_id,
            "time": trip_time if trip_time else "N/A"
        }
        if stop_type == "pickup":
            schedules[route_id]["pickup"][f"shift{shift or '1'}"].append(stop_info)
        elif stop_type == "dropoff":
            schedules[route_id]["dropoff"][f"shift{shift or '1'}"].append(stop_info)

    return render_template('view_admin_schedules.html', schedules=schedules)

    



# Define the route to add a new admin
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

@app.route('/view_users', methods=['GET', 'POST'])
def view_users():
    if 'admin_id' not in session:
        return redirect(url_for('adminlogin'))


    search_term = request.args.get('search', '')  # Get the search query from the URL parameters
   
    cursor = mysql.connection.cursor()


    if search_term:
        # If there is a search term, filter users by ID or name
        cursor.execute("SELECT * FROM users WHERE id LIKE %s OR name LIKE %s", ('%' + search_term + '%', '%' + search_term + '%'))
    else:
        # Otherwise, get all users
        cursor.execute("SELECT * FROM users")
   
    users = cursor.fetchall()
    cursor.close()


    return render_template('view_users.html', users=users, search_term=search_term)


# Define the route to remove a user
@app.route('/remove_user/<int:user_id>', methods=['POST'])
def remove_user(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('adminlogin'))


    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    mysql.connection.commit()
    cursor.close()


    flash("User removed successfully", "success")
    return redirect(url_for('view_users'))

@app.route('/view_faculty_staff')
def view_faculty_staff():
    if 'admin_id' not in session:
        return redirect(url_for('adminlogin'))
   
    search_term = request.args.get('search', '')  # Get the search query from the URL parameters


    cursor = mysql.connection.cursor()
    if search_term:
        # If there is a search term, filter staff by ID or full name
        cursor.execute("SELECT id, full_name, email FROM staffs WHERE id LIKE %s OR full_name LIKE %s",
                       ('%' + search_term + '%', '%' + search_term + '%'))
    else:
        # Otherwise, get all staff
        cursor.execute("SELECT id, full_name, email FROM staffs")


    staffs = cursor.fetchall()
    cursor.close()


    return render_template('view_faculty_staff.html', staffs=staffs, search_term=search_term)

# Route for removing staff
@app.route('/remove_staff/<int:staff_id>', methods=['POST'])
def remove_staff(staff_id):
    if 'admin_id' not in session:
        return redirect(url_for('adminlogin'))


    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM staffs WHERE id=%s", (staff_id,))
    mysql.connection.commit()
    cursor.close()


    flash("Staff member removed successfully", "success")
    return redirect(url_for('view_faculty_staff'))
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

# Define the route for updating the user's profile
@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    form = UpdateProfileForm()
    user_id = session['user_id']

    if form.validate_on_submit():
        full_name = form.full_name.data
        student_id = form.student_id.data
        department = form.department.data
        gender = form.gender.data
        address = form.address.data
        mobile_number = form.mobile_number.data
        blood_group = form.blood_group.data

        # Image upload
        if form.profile_image.data:
            image_file = form.profile_image.data
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

            cursor = mysql.connection.cursor()
            cursor.execute("""
                UPDATE users 
                SET full_name = %s, student_id = %s, department = %s, gender = %s, 
                    address = %s, mobile_number = %s, blood_group = %s, profile_image = %s 
                WHERE id = %s
            """, (full_name, student_id, department, gender, address, mobile_number, blood_group, filename, user_id))
            mysql.connection.commit()
            cursor.close()
        else:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                UPDATE users 
                SET full_name = %s, student_id = %s, department = %s, gender = %s, 
                    address = %s, mobile_number = %s, blood_group = %s 
                WHERE id = %s
            """, (full_name, student_id, department, gender, address, mobile_number, blood_group, user_id))
            mysql.connection.commit()
            cursor.close()

        # Store the success message in session
        session['profile_update_message'] = "Profile updated successfully!"
        return redirect(url_for('dashboard'))

    # Pre-fill form fields with user data
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        form.full_name.data = user[4]
        form.student_id.data = user[5]
        form.department.data = user[6]
        form.gender.data = user[12]  # Assuming "Gender" column is at index 12
        form.address.data = user[7]
        form.mobile_number.data = user[8]
        form.blood_group.data = user[9]

    return render_template('update_profile.html', form=form)



@app.route('/staff_update_profile', methods=['GET', 'POST'])
def staff_update_profile():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    form = StaffUpdateProfileForm()
    staff_id = session['staff_id']

    if form.validate_on_submit():
        full_name = form.full_name.data
        PIN = form.PIN.data
        department = form.department.data
        address = form.address.data
        mobile_number = form.mobile_number.data
        blood_group = form.blood_group.data

        # image upload
        if form.profile_image.data:
            image_file = form.profile_image.data
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

            # Update the database with the profile image path
            cursor = mysql.connection.cursor()
            cursor.execute("""
                UPDATE staffs 
                SET full_name = %s, pin = %s, department = %s, address = %s, mobile_number = %s, blood_group = %s, profile_image = %s 
                WHERE id = %s
            """, (full_name, PIN, department, address, mobile_number, blood_group, filename, staff_id))
            mysql.connection.commit()
            cursor.close()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('staff_dashboard'))

    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM staffs WHERE id = %s", (staff_id,))
        staff = cursor.fetchone()
        cursor.close()

        if staff:
            form.full_name.data = staff[4]
            form.PIN.data = staff[5]
            form.department.data = staff[6]
            form.address.data = staff[7]
            form.mobile_number.data = staff[8]
            form.blood_group.data = staff[9]

    return render_template('staff_update_profile.html', form=form)


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
        timer_duration=300  # 5 minutes timer
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

    
@app.route('/request_vehicle', methods=['GET', 'POST'])
def request_vehicle():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    form = VehicleRequestForm()
    staff_id = session['staff_id']

    if form.validate_on_submit():
        journey_date = form.journey_date.data
        pickup_time = form.pickup_time.data
        pickup_location = form.pickup_location.data
        destination = form.destination.data
        capacity = form.capacity.data

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO vehicle_requests (staff_id, journey_date, pickup_time, pickup_location, destination, capacity)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (staff_id, journey_date, pickup_time, pickup_location, destination, capacity))
        mysql.connection.commit()
        cursor.close()

        # Store success message in the session
        session['vehicle_request_message'] = "Vehicle request submitted successfully!"
        return redirect(url_for('staff_dashboard'))

    return render_template('request_vehicle.html', form=form)


@app.route('/view_requests', methods=['GET', 'POST'])
def view_requests():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    cursor = mysql.connection.cursor()
    cursor.execute("""
    SELECT vr.id, s.initial, vr.journey_date, vr.pickup_location, vr.destination, 
           vr.capacity, vr.status 
    FROM vehicle_requests vr 
    JOIN staffs s ON vr.staff_id = s.id
    ORDER BY FIELD(vr.status, 'Pending') DESC, vr.journey_date ASC
    """)
    requests = cursor.fetchall()
    cursor.close()

    return render_template('view_requests.html', requests=requests)



@app.route('/respond_request/<int:request_id>', methods=['POST'])
def respond_request(request_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    action = request.form.get("action")
    reply = request.form.get("reply")

    cursor = mysql.connection.cursor()

    if action == "approve":
        # Approve the request
        cursor.execute("""
            UPDATE vehicle_requests 
            SET status='Approved', reply=%s 
            WHERE id=%s
        """, (reply, request_id))
        message = "Your vehicle request has been approved!"
    elif action == "reject":
        # Reject the request
        cursor.execute("""
            UPDATE vehicle_requests 
            SET status='Rejected', reply=%s 
            WHERE id=%s
        """, (reply, request_id))
        message = "Your vehicle request has been rejected."

    mysql.connection.commit()

    # Fetch the staff's email and request details
    cursor.execute("""
        SELECT s.email, vr.journey_date, vr.pickup_location, vr.destination 
        FROM vehicle_requests vr 
        JOIN staffs s ON vr.staff_id = s.id 
        WHERE vr.id=%s
    """, (request_id,))
    staff_email, journey_date, pickup_location, destination = cursor.fetchone()
    cursor.close()

    # Send Email Notification
    try:
        msg = Message(
            "Vehicle Request Update",
            recipients=[staff_email],
            body=f"{message}\n\n"
                 f"Details:\n"
                 f"Journey Date: {journey_date}\n"
                 f"From: {pickup_location}\n"
                 f"To: {destination}\n"
                 f"Admin's Reply: {reply}\n\n"
                 f"Thank you for using our service!"
        )
        mail.send(msg)
        flash("Request responded and email sent successfully!", "success")
    except Exception as e:
        flash(f"Failed to send email notification: {e}", "danger")

    return redirect(url_for('view_requests'))



@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'user_id' not in session:
        flash("Please log in to submit feedback.", "danger")
        return redirect(url_for('login'))

    form = FeedbackForm()
    if form.validate_on_submit():
        user_id = session['user_id']

        # Fetch user info
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT name, email FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()

        cursor.execute("""
            INSERT INTO feedback (user_id, name, email, bus_number, feedback, rating, journey_date) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, user[0], user[1], form.bus_number.data, 
              form.feedback.data, form.rating.data, form.journey_date.data))
        mysql.connection.commit()
        cursor.close()

        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('feedback'))

    return render_template('feedback.html', form=form)


def get_feedback_from_db():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT name, email, bus_number, feedback, rating, journey_date, reply, id 
        FROM feedback ORDER BY journey_date DESC
    """)
    feedbacks = cursor.fetchall()
    cursor.close()
    return feedbacks

# Route for viewing feedback (admin-only)
@app.route('/view_feedback')
def view_feedback():
    if 'admin_id' not in session:
        flash("Admin access required.", "danger")
        return redirect(url_for('adminlogin'))

    feedbacks = get_feedback_from_db()
    average_rating = calculate_average_rating(feedbacks)
    return render_template('view_feedback.html', feedbacks=feedbacks, average_rating=average_rating)


@app.route('/reply_feedback/<int:feedback_id>', methods=['POST'])
def reply_feedback(feedback_id):
    if 'admin_id' not in session:
        flash("Admin access required.", "danger")
        return redirect(url_for('adminlogin'))

    reply_text = request.form['reply']

    # Update reply in the feedback table
    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE feedback 
        SET reply = %s 
        WHERE id = %s
    """, (reply_text, feedback_id))
    mysql.connection.commit()
    cursor.close()

    # Flash message for reply success
    flash("Reply sent successfully!", "success")
    # Redirect to view_feedback
    return redirect(url_for('view_feedback'))


def calculate_average_rating(feedbacks):
    if not feedbacks:
        return 0
    total_rating = sum(f[4] for f in feedbacks)  # Rating is at index 4
    return total_rating / len(feedbacks)


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
