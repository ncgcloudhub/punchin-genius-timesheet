from flask import Flask, render_template, request, redirect, url_for, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, login_required, logout_user, current_user
from flask_login import LoginManager
from datetime import datetime, time, timedelta
from wtforms.validators import ValidationError
from flask_wtf import FlaskForm
from wtforms import DateField, TimeField, SubmitField
from wtforms.validators import DataRequired
from flask_migrate import Migrate




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timesheet.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Add this line
db = SQLAlchemy(app)

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
    sign_out_time = db.Column(db.Time)
    delete_reason = db.Column(db.String, nullable=True)


@app.route('/')
def index():
    time_entries = []
    if current_user.is_authenticated:
        time_entries = TimeEntry.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', time_entries=time_entries)


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

    # Fetch the user's time entries
    time_entries = TimeEntry.query.filter_by(user_id=current_user.id).all()

    # Calculate the total hours for each entry
    for entry in time_entries:
        # Convert the time objects to datetime objects for today's date
        sign_in_datetime = datetime.combine(datetime.today(), entry.sign_in_time)
        sign_out_datetime = datetime.combine(datetime.today(), entry.sign_out_time)

        # Handle cases where sign-out time is on the next day (e.g., overnight work)
        if sign_out_datetime < sign_in_datetime:
            sign_out_datetime += timedelta(days=1)

        # Calculate the difference
        delta = sign_out_datetime - sign_in_datetime

        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        entry.total_hours = "{} H {} M".format(hours, minutes)

    # Calculate total hours worked
    total_seconds_worked = sum([(datetime.combine(datetime.today(), entry.sign_out_time) - datetime.combine(datetime.today(), entry.sign_in_time)).seconds for entry in time_entries])
    total_hours_worked = total_seconds_worked // 3600
    total_minutes_worked = (total_seconds_worked % 3600) // 60

    return render_template('dashboard.html', form=form, time_entries=time_entries, total_hours=total_hours_worked, total_minutes=total_minutes_worked)
    #return render_template('dashboard.html', time_entries=time_entries, total_hours=total_hours_worked, total_minutes=total_minutes_worked)
    #return render_template('time_entry.html')


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/add_time_entry', methods=['POST'])
@login_required
def add_time_entry():
    # Convert time strings to Python time objects
    sign_in_time_str = request.form['sign_in_time']
    sign_out_time_str = request.form['sign_out_time']

    sign_in_hour, sign_in_minute = map(int, sign_in_time_str.split(":"))
    sign_out_hour, sign_out_minute = map(int, sign_out_time_str.split(":"))
    
    sign_in_time_obj = time(sign_in_hour, sign_in_minute)
    sign_out_time_obj = time(sign_out_hour, sign_out_minute)

    # Create a new TimeEntry
    entry = TimeEntry(
        user_id=current_user.id,
        date=datetime.today().date(),
        sign_in_time=sign_in_time_obj,
        sign_out_time=sign_out_time_obj
    )
    print("Entered add_time_entry")
    print(f"Sign In Time String: {sign_in_time_str}")
    print(f"Sign Out Time String: {sign_out_time_str}")

    db.session.add(entry)
    db.session.commit()

    flash('Time entry added successfully!', 'success')
    return redirect(url_for('dashboard'))


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



@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != "Admin":
        flash('Access forbidden: Admins only.', 'danger')
        abort(403)

    # Fetch all users
    users = User.query.all()

    # Fetch statistics
    stats = {
        'total_users': User.query.count(),
        'total_employees': User.query.filter_by(role='Employee').count(),
        'total_managers': User.query.filter_by(role='Manager').count(),
        'total_admins': User.query.filter_by(role='Admin').count(),
    }

    return render_template('admin_dashboard.html', users=users, stats=stats)


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



# Display All Time Entries
@app.route('/admin_all_entries')
@login_required
def admin_all_entries():
    if current_user.role != "Admin":
        flash('Access forbidden: Admins only.', 'danger')
        abort(403)

    # Fetch all time entries of all users
    entries = TimeEntry.query.all()
    return render_template('admin_all_entries.html', entries=entries)


if __name__ == '__main__':
    app.run(debug=True)

#user: saiful  & saifuladmin
# gui   #pw: TimeSheet@2023
#sql:
#new_user = User(username="admin", password="Bhu!@V3nd0rTimesheet", email="saif.taxpro@outlook.com", is_admin=True)