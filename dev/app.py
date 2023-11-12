from flask import Flask, render_template, request, redirect, url_for, flash, abort, app, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from datetime import datetime, time, timedelta
from wtforms.validators import ValidationError
from flask_wtf import FlaskForm
from wtforms import DateField, TimeField, SubmitField
from wtforms.validators import DataRequired
from flask_migrate import Migrate
from collections import defaultdict
from sqlalchemy import func, extract, asc, desc
from sqlalchemy.orm import joinedload
import openai
import re
import logging
import os


# Define the path to the instance folder explicitly
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')

# Initialize the Flask app with instance configuration enabled
#app = Flask(__name__, instance_relative_config=True)
app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)
# Load configurations from the instance folder
app.config.from_pyfile('dev_config.py')


from profile import profile as profile_blueprint
app.register_blueprint(profile_blueprint, url_prefix='/profile')

from settings import settings as settings_blueprint
app.register_blueprint(settings_blueprint, url_prefix='/settings')



logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')


# Set up the OpenAI API key using the loaded configuration
openai.api_key = app.config['OPENAI_API_KEY']

db = SQLAlchemy(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timesheet.db'
#app.config['SECRET_KEY'] = 'your_secret_key_here'  # Add this line


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

migrate = Migrate(app, db)

class TimeEntryForm(FlaskForm):
    entry_date = DateField('Date', validators=[DataRequired()])
    sign_in_time = TimeField('Sign In Time', validators=[DataRequired()])
    sign_out_time = TimeField('Sign Out Time', validators=[DataRequired()])
    submit = SubmitField('Submit')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    # Roles
    role = db.Column(db.String(20), default="Employee")
    is_admin = db.Column(db.Boolean, default=False) # for Admin Dashboard
    email = db.Column(db.String(120), unique=True, nullable=False)




    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class TimeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='time_entries')
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    sign_in_time = db.Column(db.Time, nullable=False)
    sign_out_time = db.Column(db.Time, nullable=True)
    delete_reason = db.Column(db.String, nullable=True)

CLOCK_IN_PATTERNS = [
    r'clock in at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'begin my day at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'my shift start at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'check in at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'sign in at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'start working at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'start my shift at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'start work at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'started work at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'began my day at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)'
    r'start now at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)'
]


CLOCK_OUT_PATTERNS = [
    r'clock out at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'end my day at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'my shift ends at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'check out at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'sign out at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'stop working at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'end my shift at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'finish work at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'i finished work at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'i ended my day at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r"i'm done for the day at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)",
    r'finish work now at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
    r'end my shift now at (\d{1,2})(?::(\d{2}))?\s*(AM|PM)'
]




def handle_clock_out(entry_id, sign_out_time):
    """
    Handle the clock-out process for a user based on their entry_id and the provided sign_out_time.
    
    Parameters:
    - entry_id (int): The ID of the time entry the user is attempting to clock out from.
    - sign_out_time (str): The time the user is attempting to clock out.

    Returns:
    - Tuple containing a message (str) and a status (str).
    """
    # Try parsing the time in both "HH:MM" and "H PM"/"H:MM PM" formats
    try:
        # Try format "HH:MM"
        hour, minute = map(int, sign_out_time.split(':'))
        sign_out_time_obj = time(hour, minute)
    except ValueError:
        # If the above fails, try format "H PM" or "H:MM PM"
        try:
            sign_out_time_obj = datetime.strptime(sign_out_time, '%I:%M %p').time()
        except:
            sign_out_time_obj = datetime.strptime(sign_out_time, '%I %p').time()

    # Fetch the specific entry using the provided entry ID
    entry = TimeEntry.query.get(entry_id)

    # Check if the entry exists
    if not entry:
        return ("Invalid entry. Please try again.", 'danger')
    # Check if the user has already clocked out for this entry
    if entry.sign_out_time:
        return ("You've already clocked out for this entry.", 'warning')

    # Update the sign out time for the entry
    entry.sign_out_time = sign_out_time_obj
    db.session.commit()

    return ('Clocked out successfully!', 'success')

# helper functions extract_clock_in_time and extract_clock_out_time
# The logic uses the .zfill(2) method on the hour to ensure that single-digit hours are transformed into two-digit format (e.g., 5 becomes 05). If the minute is not provided, it defaults to "00", and the meridian (AM/PM) is transformed to uppercase.
def extract_time_from_command(command):
    # Use regex to extract the time from the command
    match = re.search(r'(\d{1,2})(?::(\d{1,2}))?\s*(AM|PM)', command, re.IGNORECASE)
    if match:
        hour, minute, meridian = match.groups()
        if not minute:  # If minute is not provided, default to "00"
            minute = "00"
        formatted_time = f"{hour.zfill(2)}:{minute.zfill(2)} {meridian.upper()}"  # format as HH:MM AM/PM
        return formatted_time
    return None




@app.route('/')
def index():
    time_entries = []
    if current_user.is_authenticated:
        time_entries = TimeEntry.query.filter_by(user_id=current_user.id).all()  
    
    # Print data types and values for diagnostic purposes
    for entry in time_entries:
        print(f"Sign In Time: {entry.sign_in_time} - Type: {type(entry.sign_in_time)}")
        print(f"Sign Out Time: {entry.sign_out_time} - Type: {type(entry.sign_out_time)}")
    
    print(time_entries)
    return render_template('index.html', time_entries=time_entries)



def process_interpreted_data(data):
    # Here, we'll make some assumptions on the possible outputs from GPT-4.
    # Depending on the actual outputs, you might need to adjust the logic.
    if "sign in" in data.lower():
        action = "sign_in"
    elif "sign out" in data.lower() or "clock out" in data.lower():
        action = "sign_out"
    else:
        action = None  # Unrecognized action
    
    # Extract time. This is a basic example and might not cover all cases.
    time_data = re.search(r'(\d{1,2} (AM|PM|am|pm))', data)
    if time_data:
        time_data = time_data.group(1)
    else:
        time_data = None

    return action, time_data


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()

        if user_exists:
            flash('Username already taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        if email_exists:
            flash('Email already taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        password = request.form['password']
        hashed_password = generate_password_hash(password, method='scrypt')

        new_user = User(
            username=username, 
            password=hashed_password,
            email=email,
            first_name=first_name,
            last_name=last_name
            )
        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        
        # Check if the user does not exist
        if not user:
            flash("You don't have an account. You should register an account for FREE.", 'warning')
            return redirect(url_for('register'))

        # Check if the password is correct for the existing user
        elif check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    
    form = TimeEntryForm()

    if form.validate_on_submit():
        # Logic to handle and save the form data
        entry_date = form.entry_date.data
        sign_in_time = form.sign_in_time.data
        sign_out_time = form.sign_out_time.data

    # Fetch the user's time entries and sort them by date in ascending order
    #time_entries = TimeEntry.query.filter_by(user_id=current_user.id).all()
    time_entries = TimeEntry.query.filter_by(user_id=current_user.id).order_by(TimeEntry.date.asc()).all()
    print("Total Entries:", len(time_entries))
    for entry in time_entries:
        print(entry.date, entry.sign_in_time, entry.sign_out_time)

    
    # Organizing entries by weeks
    from collections import defaultdict
    from datetime import timedelta

    entries_by_week = defaultdict(list)
    for entry in time_entries:
        # Determine the date of the Monday of the week for this entry
        sunday = entry.date - timedelta(days=(entry.date.weekday() + 1) % 7)
        entries_by_week[sunday].append(entry)

    # Compute day of the week for each entry
    for entry in time_entries:
        entry.day_of_week = entry.date.strftime('%A')  # Computes the day of the week, e.g., "Monday"
        # Convert the time objects to datetime objects for today's date
        sign_in_datetime = datetime.combine(datetime.today(), entry.sign_in_time)
        if entry.sign_out_time:
            sign_out_datetime = datetime.combine(datetime.today(), entry.sign_out_time)
            # Handle cases where sign-out time is on the next day (e.g., overnight work)
            if sign_out_datetime < sign_in_datetime:
                sign_out_datetime += timedelta(days=1)
            # Calculate the difference
            delta = sign_out_datetime - sign_in_datetime
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            entry.total_hours = hours
            entry.total_minutes = minutes
        else:
            entry.total_hours = 0
            entry.total_minutes = 0

    # Calculate total hours worked for each week
    weekly_totals = {}
    for monday, entries in entries_by_week.items():
        total_seconds = sum([(datetime.combine(datetime.today(), e.sign_out_time) - datetime.combine(datetime.today(), e.sign_in_time)).seconds if e.sign_out_time else 0 for e in entries])
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        weekly_totals[monday] = (hours, minutes)

    # Find the active entry (the most recent entry without a sign-out time)
    active_entry = None
    for entry in time_entries:
        if not entry.sign_out_time:
            if not active_entry or entry.date > active_entry.date:
                active_entry = entry

    # Fetch the user's time entries for the current month
    current_month = datetime.today().month
    current_year = datetime.today().year
    from sqlalchemy import extract
    monthly_entries = TimeEntry.query.filter_by(user_id=current_user.id).filter(extract('month', TimeEntry.date) == current_month, extract('year', TimeEntry.date) == current_year).all()

    # Calculate total hours worked for the current month
    total_seconds_monthly = sum([(datetime.combine(datetime.today(), e.sign_out_time) - datetime.combine(datetime.today(), e.sign_in_time)).seconds if e.sign_out_time else 0 for e in monthly_entries])
    monthly_total_hours = total_seconds_monthly // 3600
    monthly_total_minutes = (total_seconds_monthly % 3600) // 60

    from datetime import date
    default_date = date.today().strftime('%Y-%m-%d') # for example, today's date
    # Render the template
    return render_template('dashboard.html', form=form, entries=time_entries, entries_by_week=entries_by_week, weekly_totals=weekly_totals, default_date=default_date, monthly_total_hours=monthly_total_hours, monthly_total_minutes=monthly_total_minutes, active_entry=active_entry)
    

@app.template_filter('zfill')
def zfill_filter(s):
    return str(s).zfill(2)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/clock_in', methods=['POST'])
@login_required
def clock_in():
    # Check if the request contains JSON data
    if request.is_json:
        data = request.get_json()
        sign_in_str = extract_time_from_command(data['time'])  # Changed 'command' to 'time'
        
        if not sign_in_str:
            return jsonify({"message": "Invalid time format", "status": "error"}), 400

        sign_in_time_obj = datetime.strptime(sign_in_str, '%I:%M %p').time()
        entry_date = datetime.today().date()
    else:
        entry_date = datetime.strptime(request.form['entry_date'], '%Y-%m-%d').date()
        hours, minutes = map(int, request.form['sign_in_time'].split(':'))
        sign_in_time_obj = time(hours, minutes)


    # Fetch the most recent active entry for the user (i.e., an entry without a sign_out_time)
    active_entry = TimeEntry.query.filter_by(user_id=current_user.id, sign_out_time=None).order_by(TimeEntry.date.desc()).first()

    # If an active entry exists, don't allow clock-in
    if active_entry:  
        if request.is_json:
            return jsonify({"message": "You're already clocked in. Please clock out first.", "status": "error", "action": "alert"})
        else:
            flash("You're already clocked in. Please clock out first.")
            return redirect(url_for('dashboard', alert=True))

    
    # Convert string time to Python time object for sign_out_time (if provided)
    sign_out_time_str = request.form.get('sign_out_time')
    if sign_out_time_str:
        hours, minutes = map(int, sign_out_time_str.split(':'))
        sign_out_time_obj = time(hours, minutes)
    else:
        sign_out_time_obj = None

    # Create a new time entry
    new_time_entry = TimeEntry(
        user_id=current_user.id,
        date=entry_date,
        sign_in_time=sign_in_time_obj,
        sign_out_time=sign_out_time_obj
    )

    db.session.add(new_time_entry)
    db.session.commit()

    flash('Time entry added successfully!', 'success')
    if request.is_json:
        return jsonify({"message": "Successful clock in.", "status": "success"})
    else:
        return redirect(url_for('dashboard'))

    #return redirect(url_for('dashboard'))


@app.route('/clock_out', methods=['POST'])
@login_required
def clock_out():
    # Check if the request contains JSON data
    if request.is_json:
        data = request.get_json()
        sign_out_str = extract_time_from_command(data['time'])

        
        if not sign_out_str:
            return jsonify({"message": "Invalid time format", "status": "error"}), 400

        # Get the current user's latest time entry which hasn't been clocked out
        entry = TimeEntry.query.filter_by(user_id=current_user.id, sign_out_time=None).order_by(TimeEntry.date.desc()).first()
        if not entry:
            return jsonify({"message": "You haven't clocked in today. Clock out first", "status": "error"}), 400

        # Use the handle_clock_out function to process the clock out action
        message, status = handle_clock_out(entry.id, sign_out_str)

    else:
        entry_id = request.form.get('entry_id')
        sign_out_str = request.form.get('sign_out_time')

        # Use the handle_clock_out function to process the clock out action
        message, status = handle_clock_out(entry_id, sign_out_str)

    # Display the resulting message to the user
    flash(message, status)
    if request.is_json:
        return jsonify({"message": "Successful clock out.", "status": "success"})
    else:
        return redirect(url_for('dashboard'))


@app.route('/process_time_entry', methods=['POST'])
@login_required
def process_time_entry():
    command = request.form['time_command'].strip().lower()

    # Check clock-in patterns
    for pattern in CLOCK_IN_PATTERNS:
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            # Extract time from the matched pattern
            hour, minute, meridian = match.groups()
            if not minute:
                minute = "00"
            time_str = f"{hour.zfill(2)}:{minute} {meridian.upper()}"
            return jsonify({'status': 'success', 'action': 'clock_in', 'time': time_str})

    # Check clock-out patterns
    for pattern in CLOCK_OUT_PATTERNS:
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            # Extract time from the matched pattern
            hour, minute, meridian = match.groups()
            if not minute:
                minute = "00"
            time_str = f"{hour.zfill(2)}:{minute} {meridian.upper()}"
            return jsonify({'status': 'success', 'action': 'clock_out', 'time': time_str})

    # If no matches found, return an error
    return jsonify({'status': 'error', 'message': 'Invalid command, Please use on of the examples shown below'})


@app.route('/edit_time_entry/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_time_entry(entry_id):
    print(request.form)
    entry = TimeEntry.query.get_or_404(entry_id)

    # Ensure the entry belongs to the current user and Manager
    if entry.user_id != current_user.id and current_user.role != "Manager":
        flash('Access forbidden: Users and Managers only.', 'danger')
        abort(403)  # Forbidden

    if request.method == 'POST':
        entry.date = datetime.strptime(request.form['entry_date'], '%Y-%m-%d').date()
        entry.sign_in_time = datetime.strptime(request.form['sign_in_time'], '%H:%M').time()
        entry.sign_out_time = datetime.strptime(request.form['sign_out_time'], '%H:%M').time()
        
        db.session.commit()
        flash('Time entry updated!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_time_entry.html', entry=entry)

@app.route('/delete_time_entry/<int:entry_id>', methods=['POST'])
@login_required
def delete_time_entry(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    
    # Ensure the entry belongs to the current user
    if entry.user_id != current_user.id and current_user.role != "Manager":
        flash('Access forbidden: Users and Managers only.', 'danger')
        abort(403)  # Forbidden

    delete_reason = request.form.get('delete_reason')
    if not delete_reason:
        flash('Please provide a reason for deletion.', 'danger')
        return redirect(url_for('dashboard'))
    entry.delete_reason = delete_reason    
    db.session.delete(entry)
    db.session.commit()
    flash('Time entry has been deleted!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/admin_dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    if current_user.role != "Admin":
        flash('Access forbidden: Admins only.', 'danger')
        abort(403)
    
    monthly_hours = get_monthly_hours_for_all_users()
    # Fetch all users
    users = User.query.all()

    # Fetch statistics
    stats = {
        'total_users': User.query.count(),
        'total_employees': User.query.filter_by(role='Employee').count(),
        'total_managers': User.query.filter_by(role='Manager').count(),
        'total_admins': User.query.filter_by(role='Admin').count(),
    }

    return render_template('admin_dashboard.html', users=users, stats=stats, monthly_hours=monthly_hours)


@app.route('/change_role/<int:user_id>', methods=['POST'])
@login_required
def change_role(user_id):
    if current_user.role != "Admin":
        flash('Access forbidden: Admins only.', 'danger')
        return redirect(url_for('index'))
    user = User.query.get(user_id)
    new_role = request.form['new_role']
    user.role = new_role
    db.session.commit()
    flash('Role updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'Admin':
        abort(403)
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin_reset_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_reset_password(user_id):
    if current_user.role != "Admin":
        flash('Access forbidden: Admins only.', 'danger')
        abort(403)

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        new_password = request.form['new_password']
        user.password = generate_password_hash(new_password, method='scrypt')
        db.session.commit()
        flash(f"Password for {user.username} has been reset.", 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_reset_password.html', user=user)

@app.route('/manager_dashboard')
@login_required
def manager_dashboard():
    if current_user.role != "Manager":
        flash('Access forbidden: Managers only.', 'danger')
        abort(403)

     # Fetch all time entries of employees only
    time_entries = TimeEntry.query.join(User, TimeEntry.user_id == User.id).filter(User.role == 'Employee').all()
    
    return render_template('manager_dashboard.html', time_entries=time_entries)



@app.route('/manager_view_users')
@login_required
def manager_view_users():
    if current_user.role != "Manager":
        flash('Access forbidden: Managers only.', 'danger')
        abort(403)
    users = User.query.filter_by(role='Employee').all()
    return render_template('manager_view_users.html', users=users)

@app.route('/manager_change_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def manager_change_password(user_id):
    if current_user.role != "Manager":
        flash('Access forbidden: Managers only.', 'danger')
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        new_password = request.form['new_password']
        user.password = generate_password_hash(new_password, method='scrypt')
        db.session.commit()
        flash(f"Password for {user.username} has been changed.", 'success')
        return redirect(url_for('manager_view_users'))

    return render_template('manager_change_password.html', user=user)

@app.route('/manager_view_time_entries/<int:user_id>', methods=['GET'])
@login_required
def manager_view_time_entries(user_id):
    if current_user.role != "Manager":
        flash('Access forbidden: Managers only.', 'danger')
        abort(403)
    time_entries = TimeEntry.query.filter_by(user_id=user_id).all()
    return render_template('manager_time_entries.html', time_entries=time_entries)

@app.route('/manager_all_entries')
@login_required
def manager_all_entries():
    if current_user.role != "Manager":
        flash('Access forbidden: Managers only.', 'danger')
        abort(403)

    # Fetch all time entries of all employees
    entries = TimeEntry.query.all()
    return render_template('manager_all_entries.html', entries=entries)


@app.route('/admin_update_roles', methods=['GET', 'POST'])
@login_required
def admin_update_roles():
    if current_user.role != "Admin":
        flash('Access forbidden: Admins only.', 'danger')
        abort(403)
    
    users = User.query.all()
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        new_role = request.form.get('new_role')
        user = User.query.get(user_id)
        user.role = new_role
        db.session.commit()
        flash('Role updated successfully!', 'success')
        return redirect(url_for('admin_update_roles'))

    return render_template('admin_update_roles.html', users=users)


@app.route('/admin_all_entries')
@login_required
def admin_all_entries():
    if current_user.role != "Admin":
        flash('Access forbidden: Admins only.', 'danger')
        abort(403)


    # Capture sort parameters
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'asc')
    order_func = asc if sort_order == 'asc' else desc

    # Capture filter parameters
    date_filter = request.args.get('date_filter', None)
    username_filter = request.args.get('username_filter')

    # Start with a base query that joins with the User table
    query = db.session.query(TimeEntry).join(User, TimeEntry.user_id == User.id)

    # Apply date filter if it exists
    if date_filter:
        query = query.filter(TimeEntry.date == date_filter)
    
    # Apply username filter if it exists
    if username_filter:
        query = query.filter(User.username == username_filter)

    # Apply sorting
    if hasattr(TimeEntry, sort_by) or hasattr(User, sort_by):
        model = TimeEntry if hasattr(TimeEntry, sort_by) else User
        query = query.order_by(order_func(getattr(model, sort_by)))

    entries = query.all()

    users = User.query.all()
    return render_template('admin_all_entries.html', entries=entries, users=users)





# Database Query: We'll create a query that aggregates the total hours worked by each user for the current month.
def get_monthly_hours_for_all_users():
    # Fetch data for all months
    results = db.session.query(
        User.username, 
        extract('month', TimeEntry.date).label('month'),
        func.sum((func.strftime('%H', TimeEntry.sign_out_time) - func.strftime('%H', TimeEntry.sign_in_time))*3600 + (func.strftime('%M', TimeEntry.sign_out_time) - func.strftime('%M', TimeEntry.sign_in_time))*60).label('total_seconds')
    ).join(TimeEntry, TimeEntry.user_id == User.id).group_by(User.username, extract('month', TimeEntry.date)).all()

    # Convert results into a structured dictionary
    monthly_data = defaultdict(dict)
    for username, month, seconds in results:
        monthly_data[int(month)][username] = seconds

    return monthly_data

if __name__ == '__main__':
    app.run(debug=True)

print(app.instance_path)
