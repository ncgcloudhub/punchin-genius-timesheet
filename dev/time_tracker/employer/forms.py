# \employer\forms.py
#
from django import forms
# Assuming TimeEntry model is in employer/models.py
from core.models import TimeEntry
from .models import Employer, Invitation
from django.contrib.auth import get_user_model
# from core.forms import RegisterForm
# from .forms import EmployerRegistrationForm


class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        # Replace with actual field names
        fields = ['clock_in', 'clock_out', 'description', 'project']


class EmployerRegistrationForm(forms.ModelForm):
    # If you want to use a separate field for username
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Employer
        fields = ['employer_name', 'employer_email_address',
                  'employer_phone_number']

    def save(self, commit=True):
        employer = super().save(commit=False)
        # Here you can handle the creation of the user account with the username and password
        if commit:
            employer.save()
        return employer


class EmployerInvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['email']
