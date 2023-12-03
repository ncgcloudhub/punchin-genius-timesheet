from flask import render_template, request, redirect, url_for, flash
from . import settings  # This imports the Blueprint from the __init__.py in the same directory
from flask_login import login_required
from .forms import UserSettingsForm  # Import the form at the top of your routes file


@settings.route('/')
@login_required
def settings_home():
    # Render your template here
    pass
    # Some logic to fetch current user settings, if needed
    return render_template('settings/settings_home.html')



@settings.route('/update', methods=['POST'])
@login_required
def update_settings():
    # Update the user's settings here
    pass
    # Logic to update user settings
    new_setting = request.form.get('some_setting_field')
    
    try:
        # Save the new setting to the database
        # db.session.commit() or however you're handling DB commits
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings.settings_home'))
    except Exception as e:
        # Handle the exception here
        flash('An error occurred while updating your settings: {}'.format(str(e)), 'error')
        return redirect(url_for('settings.settings_home'))


from .forms import UserSettingsForm  # Import the form at the top of your routes file

@settings.route('/user_settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    form = UserSettingsForm()

    if form.validate_on_submit():
        # Here, you would typically update the user's settings in the database.
        # For this example, I'm just going to flash a success message.
        flash('User settings have been updated!', 'success')
        return redirect(url_for('settings.user_settings'))

    return render_template('settings/user_settings.html', form=form)

