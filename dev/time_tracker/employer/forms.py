# \employer\forms.py
#
from django import forms
# Assuming TimeEntry model is in employer/models.py
from core.models import TimeEntry
from .models import Employer, Invitation
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import logging

logger = logging.getLogger(__name__)


class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        # Replace with actual field names
        fields = ['clock_in', 'clock_out', 'description', 'project']


class EmployerRegistrationForm(forms.ModelForm):
    agree_terms = forms.BooleanField(
        label=mark_safe(
            'I agree to the <a href="/path-to-terms-and-conditions" target="_blank">terms and conditions</a>'),
        required=True
    )

    class Meta:
        model = Employer
        fields = [
            'employer_name', 'employer_email_address', 'employer_phone_number',
            'employer_address', 'employer_city', 'employer_state', 'employer_zip_code',
            'employer_ein_number'
        ]

    def __init__(self, *args, **kwargs):
        """Initialize form with custom settings for placeholders and classes."""
        super(EmployerRegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[field].label
            })
        self.fields['agree_terms'].widget.attrs.update({'class': ''})

    def save(self, commit=True):
        """Save the employer instance and create a user account with hashed password."""
        employer = super().save(commit=False)
        user = None
        if commit:
            try:
                # Handle the user creation with hashed password
                user = User.objects.create(
                    username=employer.employer_email_address,
                    email=employer.employer_email_address,
                    password=make_password(self.cleaned_data["password"])
                )
                employer.user = user
                employer.save()
            except Exception as e:
                logger.error(f"Error saving employer or creating user: {e}")
                raise ValidationError("Failed to register employer and user")
        return employer


class EmployerInvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['email']
