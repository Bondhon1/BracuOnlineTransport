
from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, FileField
from wtforms.validators import Length, DataRequired, Email, ValidationError
import bcrypt
from flask_mysqldb import MySQL
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import TimeField


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


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()]) 
    password = PasswordField("Password", validators=[DataRequired()])  
    submit = SubmitField("Login")

class AdminLoginForm(FlaskForm):
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
        
class AddScheduleForm(FlaskForm):
    route_name = StringField("Route Name", validators=[DataRequired()])
    departure_time = TimeField("Departure Time", format='%H:%M', validators=[DataRequired()])
    arrival_time = TimeField("Arrival Time", format='%H:%M', validators=[DataRequired()])
    bus_number = StringField("Bus Number", validators=[DataRequired()])
    driver_name = StringField("Driver Name")
    capacity = IntegerField("Capacity")
    submit = SubmitField("Add Schedule")


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
            return redirect(url_for('Admindashboard'))  # Redirect to the admin dashboard
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

# Define the route for the user dashboard
@app.route('/admin_dashboard')
def Admindashboard():
    if 'admin_id' in session:  # Check if the admin is logged in (admin_id in session)
        admin_id = session['admin_id']  # Get the admin_id from the session

        # Query the database to find the admin's details
        cursor = mysql.connection.cursor()  # Create a cursor to interact with the database
        cursor.execute("SELECT name, email FROM admins WHERE admin_id = %s", (admin_id,))  # Query to find the admin by ID
        admin = cursor.fetchone()  # Fetch one record
        cursor.close()  # Close the cursor

        if admin:
            return render_template('admin_dashboard.html', admin=admin)  # Render the dashboard with admin details
    else:
        return redirect(url_for('adminlogin'))  # Redirect to the login page if not logged in

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
        cursor.execute("INSERT INTO admins (username, email, password) VALUES (%s, %s, %s)",
                       (username, email, password))
        mysql.connection.commit()
        cursor.close()

        flash('New admin added successfully!', 'success')
        return redirect(url_for('Admindashboard'))

    return render_template('add_admin.html', form=form)

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
# Define the route for logging out the user

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

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove the user's ID from the session to log out
    flash("You have been logged out successfully.")  # Flash a success message
    return redirect(url_for('login'))  # Redirect to the login page

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_id', None)  # Remove the admin's ID from the session to log out
    flash("Admin has been logged out successfully.")  # Flash a success message
    return redirect(url_for('adminlogin'))  # Redirect to the admin login page

# Run the Flask application with debug mode enabled
if __name__ == '__main__':
    app.run(debug=True)
