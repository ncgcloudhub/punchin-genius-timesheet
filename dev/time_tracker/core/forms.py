# core/forms.py --> app specific forms

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
# from .models import Employer, EmployeeProfile, PunchinUser, TimeEntry
from .models import EmployeeProfile, PunchinUser, TimeEntry
from django.apps import apps


if apps.is_installed('employer'):
    from employer.models import Invitation


User = get_user_model()


class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['clock_in', 'clock_out', 'description', 'project']


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'First Name'}), required=True)
    middle_initial = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Middle Initial'}), required=False)
    last_name = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Last Name'}), required=True)
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'placeholder': 'Email'}), required=True)
    phone_number = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Phone Number'}), required=True)
    agree_terms = forms.BooleanField(
        # Added the asterisk here in label
        label="Agree to terms and conditions *", required=True)

    class Meta:
        model = PunchinUser
        fields = [
            'first_name', 'middle_initial', 'last_name', 'phone_number', 'email',
            'password1', 'password2', 'agree_terms'
        ]

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        # Update placeholder attributes for each field
        for field_name, field in self.fields.items():
            if field.required:
                placeholder = field.widget.attrs.get(
                    'placeholder', field.label)
                field.widget.attrs['placeholder'] = f"{placeholder} *"
            field.label = ''  # Remove the labels since you're using placeholders
            if field_name == 'email':
                # Example for custom placeholder
                field.widget.attrs['placeholder'] = 'E-Mail Address (Username) *'
            elif field_name == 'password1':
                field.widget.attrs['placeholder'] = 'Password *'
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = 'Password confirmation *'
            elif field_name == 'agree_terms':
                field.label = "Agree to terms and conditions *"


class EmployeeLinkForm(forms.Form):
    invitation_token = forms.CharField(max_length=255)

    def clean_invitation_token(self):
        token = self.cleaned_data.get('invitation_token')
        if apps.is_installed('employer'):
            # Perform the checks and validation using the Invitation model
            try:
                invitation = Invitation.objects.get(token=token)
                # ... rest of your validation logic
            except Invitation.DoesNotExist:
                raise forms.ValidationError("Invalid invitation token.")
        else:
            # Handle cases when employer app is not installed.
            # Maybe raise a validation error or provide a default behavior.
            raise forms.ValidationError(
                "Invitation functionality not available.")
        return token
