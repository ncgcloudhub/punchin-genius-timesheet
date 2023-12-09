from django import forms
from .models import TimeEntry
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import PunchinUser

User = get_user_model()


class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['clock_in', 'clock_out', 'description', 'project']


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'First name'}))
    middle_initial = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Middle initial'}), required=False)
    last_name = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Last name'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'placeholder': 'Email'}))
    phone_number = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Phone number'}), required=True)
    agree_terms = forms.BooleanField(label="Agree to terms and conditions")

    class Meta:
        model = PunchinUser
        fields = ['username', 'first_name', 'middle_initial',
                  'last_name', 'email', 'phone_number', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        # This will set the placeholder attribute for username and password fields
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Password confirmation'

        # This will remove the labels from being rendered
        for fieldname in ['username', 'first_name', 'middle_initial', 'last_name', 'email', 'phone_number', 'password1', 'password2']:
            self.fields[fieldname].label = False
