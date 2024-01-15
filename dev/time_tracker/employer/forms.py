# \employer\forms.py

from .models import Employer, EmployerProfile
from django import forms
# Assuming TimeEntry model is in employer/models.py
from core.models import TimeEntry
from .models import Employer, Invitation
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
# from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import logging
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.phonenumber import PhoneNumber as OriginalPhoneNumber


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
    employer_phone_number = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(initial='US'),
        help_text='Enter a valid phone number (e.g. 2125552368).'
    )
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(
        widget=forms.PasswordInput, label='Confirm Password')
    agree_terms = forms.BooleanField(
        label=mark_safe(
            'I agree to the <a href="/terms" target="_blank">terms and conditions</a>'),
        required=True
    )

    class Meta:
        model = Employer
        fields = ['employer_name', 'employer_address', 'employer_city',
                  'employer_state', 'employer_zip_code', 'employer_ein_number',
                  'employer_phone_number', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords don't match")
        return cleaned_data

    def save(self, commit=True):
        UserModel = get_user_model()
        user = UserModel.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        employer = super().save(commit=False)
        employer.user = user
        if commit:
            employer.save()
            EmployerProfile.objects.create(user=user, employer=employer)
        return employer

    def clean_email(self):
        email = self.cleaned_data.get('email').strip()
        UserModel = get_user_model()
        if UserModel.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email

    def clean_employer_phone_number(self):
        phone_number = self.cleaned_data.get('employer_phone_number')
        if not phone_number.is_valid():
            raise ValidationError(
                'Enter a valid phone number with the country code.')
        return phone_number


class EmployerInvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['email']
