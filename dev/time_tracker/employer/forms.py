# \employer\forms.py
#
from django import forms
# Assuming TimeEntry model is in employer/models.py
from core.models import TimeEntry
from .models import Employer, Invitation


class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        # Replace with actual field names
        fields = ['clock_in', 'clock_out', 'description', 'project']


class EmployerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Employer
        fields = ['name', 'contact_email', 'contact_phone_number']


class EmployerInvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['email']
