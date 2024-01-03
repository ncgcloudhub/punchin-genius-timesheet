# /core/admin.py

from .models import EmployeeProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from .models import PunchinUser, TimeEntry
from employer.models import Employer

# Inline definition


class EmployeeProfileInline(admin.StackedInline):
    # Define an inline admin descriptor for EmployeeProfile model
    # which acts a bit like a singleton
    model = EmployeeProfile  # Update this to your EmployeeProfile model
    can_delete = False
    verbose_name_plural = 'employee_profile'


class EmployerInline(admin.StackedInline):
    # Define an inline admin descriptor for Employer model
    model = Employer
    can_delete = False
    verbose_name_plural = 'employers'
    extra = 1


class UserAdmin(BaseUserAdmin):
    inlines = (EmployerInline, EmployeeProfileInline)

    # Since PunchinUser uses 'email' instead of 'username', adjust fields accordingly
    list_display = ('email', 'first_name', 'last_name',
                    'is_active', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        # Add more fields here if needed
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(PunchinUser, UserAdmin)
admin.site.register(TimeEntry)
