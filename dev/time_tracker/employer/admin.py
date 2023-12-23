# employer/admin.py

from django.contrib import admin
from .models import Employer
from django import forms

# Register your models here.


# You may want to create a custom form for the admin to use, including placeholders
class EmployerAdminForm(forms.ModelForm):
    class Meta:
        model = Employer
        fields = '__all__'
        widgets = {
            'employer_address': forms.TextInput(attrs={'placeholder': '123 Main St'}),
            'employer_city': forms.TextInput(attrs={'placeholder': 'Anytown'}),
            'employer_state': forms.TextInput(attrs={'placeholder': 'State'}),
            'employer_zip_code': forms.TextInput(attrs={'placeholder': '12345'}),
            'employer_ein_number': forms.TextInput(attrs={'placeholder': '12-3456789'}),
            # Add any other widgets for fields as needed
        }


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    # Add other fields you want to display in the admin list view
    list_display = ('employer_id', 'employer_name', 'employer_address', 'employer_city', 'employer_state',
                    'employer_zip_code', 'employer_email_address', 'employer_phone_number', 'employer_ein_number')
    readonly_fields = ('employer_id',)
    fields = ('employer_id', 'user', 'employer_name', 'employer_address', 'employer_city', 'employer_state',
              'employer_zip_code', 'employer_email_address', 'employer_phone_number', 'employer_ein_number')
    # Make sure the 'fields' attribute includes the new fields in the desired order


# If you have an EmployerInline, you may want to update it as well
class EmployerInline(admin.StackedInline):
    model = Employer
    can_delete = False
    verbose_name_plural = 'employer'
    # Include the additional fields if you want them in the inline as well
    fields = ('employer_id', 'employer_name', 'employer_email_address', 'employer_phone_number',
              'employer_address', 'employer_city', 'employer_state', 'employer_zip_code', 'employer_ein_number')
    readonly_fields = ('employer_id',)
