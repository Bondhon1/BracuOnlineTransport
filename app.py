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


class AddAdminForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])  
    email = StringField("Email", validators=[DataRequired(), Email()])  
    password = PasswordField("Password", validators=[DataRequired()])  
    submit = SubmitField("Add Admin") 

# Feedback form class using Flask-WTF and WTForms
class FeedbackForm(FlaskForm):
    bus_number = StringField('Bus Number', validators=[DataRequired()])
    feedback = TextAreaField('Feedback', validators=[DataRequired(), Length(min=10, max=500)])
    rating = IntegerField('Rating (1-5)', validators=[DataRequired()])
    journey_date = DateField('Journey Date', validators=[DataRequired()])
    submit = SubmitField('Submit Feedback')
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = mysql.connection.cursor()
    today = date.today().strftime('%Y-%m-%d')

    # Fetch user details
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

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
@app.route('/add_feedback/<route_name>/<journey_date>', methods=['GET', 'POST'])
def add_feedback(route_name, journey_date):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        rating = request.form.get('rating')
        feedback = request.form.get('feedback')

        cursor = mysql.connection.cursor()

        # Fetch username and email for the user
        cursor.execute("SELECT name, email FROM users WHERE id = %s", (user_id,))
        user_details = cursor.fetchone()
        if not user_details:
            flash("Unable to fetch user details. Please contact admin.", "danger")
            return redirect(url_for('dashboard'))

        username, email = user_details

        # Insert feedback with username and email
        cursor.execute("""
            INSERT INTO feedback (user_id, name, email, route_name, journey_date, rating, feedback)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, username, email, route_name, journey_date, rating, feedback))
        mysql.connection.commit()
        cursor.close()

        flash("Feedback submitted successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_feedback.html', route_name=route_name, journey_date=journey_date)

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
        FROM feedback
    """)
    feedbacks = cursor.fetchall()
    cursor.close()
    return feedbacks

def calculate_average_rating(feedbacks):
    if not feedbacks:
        return 0
    total_rating = sum(f[4] for f in feedbacks)  # Rating is at index 4
    return total_rating / len(feedbacks)
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

    flash("Reply sent successfully!", "success")
    return redirect(url_for('view_feedback'))



# Run the Flask application with debug mode enabled
if __name__ == '__main__':
    app.run(debug=True)
