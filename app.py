
from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, FileField, TextAreaField, DateField
from wtforms.validators import Length, DataRequired, Email, ValidationError, InputRequired
import bcrypt
from flask_mysqldb import MySQL
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import TimeField
from wtforms import SelectField, FloatField, TimeField
from flask import jsonify, request


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads' 
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  


app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root'     
app.config['MYSQL_PASSWORD'] = ''       
app.config['MYSQL_DB'] = 'mydatabase'  
app.secret_key = 'your_secret_key_here'

mysql = MySQL(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


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
            raise ValidationError('PIN must be exactly 8 digits long.')
        

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
    journey_date = StringField("Journey Date", validators=[DataRequired()])
    pickup_location = StringField("Pickup Location", validators=[DataRequired()])
    destination = StringField("Destination", validators=[DataRequired()])
    capacity = IntegerField("Capacity", validators=[DataRequired()])
    submit = SubmitField("Request Vehicle")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm() 
    if form.validate_on_submit():  
        name = form.name.data 
        email = form.email.data  
        password = form.password.data  

       
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

       
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                       (name, email, hashed_password)) 
        mysql.connection.commit() 
        cursor.close() 

        return redirect(url_for('login'))

    return render_template('register.html', form=form)  

@app.route('/staff_register', methods=['GET', 'POST'])
def staff_register():
    form = StaffRegisterForm() 
    if form.validate_on_submit():  
        initial = form.initial.data 
        email = form.email.data  
        password = form.password.data  

       
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

       
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO staffs (initial, email, password) VALUES (%s, %s, %s)", 
                       (initial, email, hashed_password)) 
        mysql.connection.commit() 
        cursor.close() 

        return redirect(url_for('staff_login'))

    return render_template('staff_register.html', form=form)  

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
    if 'user_id' in session:
        user_id = session['user_id']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('dashboard.html', user=user)

    return redirect(url_for('login'))

@app.route('/staff_dashboard')
def staff_dashboard():
    if 'staff_id' in session:
        staff_id = session['staff_id']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM staffs WHERE id=%s", (staff_id,))
        staff = cursor.fetchone()
        cursor.close()

        if staff:
            return render_template('staff_dashboard.html', staff=staff)

    return redirect(url_for('satff_login'))


# Define the route for the user dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' in session:
        admin_id = session['admin_id']

        # Fetch admin details
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT name, email FROM admins WHERE admin_id = %s", (admin_id,))
        admin = cursor.fetchone()

        # Fetch analytics data
        cursor.execute("SELECT (SELECT COUNT(*) FROM users) + (SELECT COUNT(*) FROM staffs)")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vehicle_requests WHERE status = 'Pending'")
        pending_requests = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM feedback WHERE reply IS NULL")
        pending_feedback = cursor.fetchone()[0]
        
        cursor.close()

        return render_template(
            'admin_dashboard.html', 
            admin=admin, 
            total_users=total_users, 
            pending_requests=pending_requests, 
            pending_feedback=pending_feedback
        )
    else:
        return redirect(url_for('adminlogin'))

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

   

# Define the route to view users
@app.route('/view_users')
def view_users():
    if 'admin_id' not in session:
        return redirect(url_for('adminlogin'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()

    return render_template('view_users.html', users=users)

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
        address = form.address.data
        mobile_number = form.mobile_number.data
        blood_group = form.blood_group.data

        # Handle profile image upload
        if form.profile_image.data:
            image_file = form.profile_image.data
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

            # Update the database with the profile image path
            cursor = mysql.connection.cursor()
            cursor.execute("""
                UPDATE users 
                SET full_name = %s, student_id = %s, department = %s, address = %s, mobile_number = %s, blood_group = %s, profile_image = %s 
                WHERE id = %s
            """, (full_name, student_id, department, address, mobile_number, blood_group, filename, user_id))
            mysql.connection.commit()
            cursor.close()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            form.full_name.data = user[4]
            form.student_id.data = user[5]
            form.department.data = user[6]
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

        # Handle profile image upload
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

@app.route('/request_vehicle', methods=['GET', 'POST'])
def request_vehicle():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    form = VehicleRequestForm()
    staff_id = session['staff_id']

    if form.validate_on_submit():
        journey_date = form.journey_date.data
        pickup_location = form.pickup_location.data
        destination = form.destination.data
        capacity = form.capacity.data

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO vehicle_requests (staff_id, journey_date, pickup_location, destination, capacity)
            VALUES (%s, %s, %s, %s, %s)
        """, (staff_id, journey_date, pickup_location, destination, capacity))
        mysql.connection.commit()
        cursor.close()

        flash("Vehicle request submitted successfully!", "success")
        return redirect(url_for('staff_dashboard'))

    return render_template('request_vehicle.html', form=form)
@app.route('/view_requests')
def view_requests():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    cursor = mysql.connection.cursor()
    cursor.execute("""
    SELECT vr.id, s.initial, vr.journey_date, vr.pickup_location, vr.destination, 
           vr.capacity, vr.status 
    FROM vehicle_requests vr 
    JOIN staffs s ON vr.staff_id = s.id
""")
    requests = cursor.fetchall()
    cursor.close()

    return render_template('view_requests.html', requests=requests)


@app.route('/respond_request/<int:request_id>', methods=['POST'])
def respond_request(request_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    reply = request.form.get("reply")
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE vehicle_requests SET status='Approved', reply=%s WHERE id=%s", (reply, request_id))
    mysql.connection.commit()
    cursor.close()

    flash("Request responded successfully!", "success")
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

        # Insert feedback into the database
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
        FROM feedback
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


# Route to handle feedback reply
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

    flash("Reply sent successfully!", "success")
    return redirect(url_for('view_feedback'))



# Helper function to calculate average rating
def calculate_average_rating(feedbacks):
    if not feedbacks:
        return 0
    total_rating = sum(f[4] for f in feedbacks)  # Rating is at index 4
    return total_rating / len(feedbacks)


@app.route('/book_ticket')
def book_ticket():
    return render_template('book_ticket.html')




@app.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule():
    if 'admin_id' not in session:
        return redirect(url_for('adminlogin'))

    form = AddScheduleForm()

    if form.validate_on_submit():
        route_name = form.route_name.data
        departure_time = form.departure_time.data
        arrival_time = form.arrival_time.data
        bus_number = form.bus_number.data
        driver_name = form.driver_name.data
        capacity = form.capacity.data

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO bus_schedules (route_name, departure_time, arrival_time, bus_number, driver_name, capacity)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (route_name, departure_time, arrival_time, bus_number, driver_name, capacity))
        mysql.connection.commit()
        cursor.close()

        flash("Bus schedule added successfully!", "success")
        return redirect(url_for('view_schedules'))

    return render_template('add_schedule.html', form=form)

# Route to View Schedules
@app.route('/view_schedules')
def view_schedules():
    if 'admin_id' not in session:
        return redirect(url_for('adminlogin'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM bus_schedules")
    schedules = cursor.fetchall()
    cursor.close()

    return render_template('view_schedules.html', schedules=schedules)

# Route to Delete a Schedule
@app.route('/delete_schedule/<int:schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):
    if 'admin_id' not in session:
        return redirect(url_for('adminlogin'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM bus_schedules WHERE id=%s", (schedule_id,))
    mysql.connection.commit()
    cursor.close()

    flash("Schedule deleted successfully.", "success")
    return redirect(url_for('view_schedules'))
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
        departure_time = request.form['departure_time']
        arrival_time = request.form['arrival_time']
        fare = request.form['fare']
        seat_numbers = request.form['seat_numbers']
        male_seats = request.form['male_seats']
        female_seats = request.form['female_seats']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO route_stops (route_id, stop_name, pickup_time, dropoff_time, fare, seat_numbers, male_seats, female_seats)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (bus_id, stop_name, departure_time, arrival_time, fare, seat_numbers, male_seats, female_seats))
        mysql.connection.commit()
        cursor.close()

        flash('Bus stop added successfully!', 'success')
        return redirect(url_for('Admindashboard'))


    # Fetch bus routes for selection
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT route_id, route_name FROM bus_routes")
    buses = cursor.fetchall()
    cursor.close()

    return render_template('add_bus_stop.html', buses=buses)

@app.route('/payment')
def payment():
    return render_template('payment.html')

# Route for processing payment
@app.route('/process_payment', methods=['POST'])
def process_payment():
    name = request.form['name']
    email = request.form['email']
    phone_number = request.form['phone_number']
    amount = request.form['amount']

    # Insert payment details into the database
    cursor = mysql.connection.cursor()
    cursor.execute('''
        INSERT INTO payments (name, email, phone_number, amount, status)
        VALUES (%s, %s, %s, %s, %s)
    ''', (name, email, phone_number, amount, 'successful'))
    mysql.connection.commit()
    cursor.close()

    flash('Payment successful!', 'success')
    return redirect(url_for('payment'))

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
