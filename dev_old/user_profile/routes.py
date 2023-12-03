# Profile Routes
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from .forms import UserProfileForm  # Assuming you have a form for profile updates
from . import profile

@profile.route('/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    form = UserProfileForm()
    
    # If user submits the form to update profile
    if form.validate_on_submit():
        # Get the data from form and update the user's data in the database
        current_user.username = form.username.data
        current_user.email = form.email.data
        # ... and so on for other fields

        # Save the changes to the database
        db.session.commit()  # Assuming you're using SQLAlchemy

        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile.user_profile'))  # Redirect to the profile page

    # If the request is GET, populate the form with current user data
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        # ... and so on for other fields

    return render_template('profile.html', title='User Profile', form=form)

