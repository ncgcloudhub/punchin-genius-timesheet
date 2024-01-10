# \employer\forms.py

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
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.phonenumber import PhoneNumber as OriginalPhoneNumber
from .models import EmployerProfile


logger = logging.getLogger(__name__)


# Add this new PhoneNumber class
class PhoneNumber(OriginalPhoneNumber):
    def __str__(self):
        return self.as_national


class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        # Replace with actual field names
        fields = ['clock_in', 'clock_out', 'description', 'project']


class EmployerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)  # Add this line
    password_confirm = forms.CharField(
        widget=forms.PasswordInput, label='Confirm Password')
    agree_terms = forms.BooleanField(
        label=mark_safe(
            'I agree to the <a href="/path-to-terms-and-conditions" target="_blank">terms and conditions</a>'),
        required=True
    )
    employer_phone_number = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(initial='US'),
        help_text='Enter a valid phone number (e.g. +12125552368).'
    )

    class Meta:
        model = Employer
        fields = [
            'employer_name', 'employer_email_address', 'employer_phone_number',
            'employer_address', 'employer_city', 'employer_state', 'employer_zip_code',
            'employer_ein_number', 'password'  # Add 'password' to this list
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords don't match")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(EmployerRegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[field].label
            })
        self.fields['agree_terms'].widget.attrs.update({'class': ''})

    def save(self, commit=True):
        employer = super().save(commit=False)
        if commit:
            try:
                user = User.objects.filter(
                    email=employer.employer_email_address).first()
                if not user:
                    user = User.objects.create_user(
                        username=employer.employer_email_address,
                        email=employer.employer_email_address,
                        password=self.cleaned_data.get("password")
                    )
                    user.save()

                employer.user = user
                employer.save()  # Now you can save the employer instance
                EmployerProfile.objects.create(user=user)
            except Exception as e:
                logger.error(f"Error creating user for employer: {e}")
                raise ValidationError(f"Error creating user: {e}")
        return employer


class EmployerInvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['email']
