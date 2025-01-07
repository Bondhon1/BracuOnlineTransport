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

# Feedback form class using Flask-WTF and WTForms
class FeedbackForm(FlaskForm):
    bus_number = StringField('Bus Number', validators=[DataRequired()])
    feedback = TextAreaField('Feedback', validators=[DataRequired(), Length(min=10, max=500)])
    rating = IntegerField('Rating (1-5)', validators=[DataRequired()])
    journey_date = DateField('Journey Date', validators=[DataRequired()])
    submit = SubmitField('Submit Feedback')

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


def send_email_notification(recipient, subject, message):
    try:
        msg = Message(subject, recipients=[recipient])
        msg.body = message
        mail.send(msg)
        print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {e}")

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

def calculate_average_rating(feedbacks):
    if not feedbacks:
        return 0
    total_rating = sum(f[4] for f in feedbacks)  
    return total_rating / len(feedbacks)
def send_email_notification(recipient, subject, message):
    try:
        msg = Message(subject, recipients=[recipient])
        msg.body = message
        mail.send(msg)
        print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {e}")


# Run the Flask application with debug mode enabled
if __name__ == '__main__':
    app.run(debug=True)
