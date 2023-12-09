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
    class Meta:
        model = PunchinUser
        fields = ["username", "password1", "password2"]