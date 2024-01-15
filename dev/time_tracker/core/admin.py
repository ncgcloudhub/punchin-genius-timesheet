# /core/admin.py

# from django.contrib.auth.models import User

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import PunchinUser, TimeEntry, EmployeeProfile
from django.apps import apps

# Get the custom user model
UserModel = get_user_model()


class EmployeeProfileInline(admin.StackedInline):
    # Define an inline admin descriptor for EmployeeProfile model
    # which acts a bit like a singleton
    model = EmployeeProfile  # Update this to your EmployeeProfile model
    can_delete = True
    verbose_name_plural = 'employee_profile'


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name',
                    'is_active', 'is_staff', 'is_employer')
    list_filter = ('is_staff', 'is_superuser', 'is_employer', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active',
         'is_staff', 'is_employer', 'is_superuser')}),
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

    # Start with just the EmployeeProfileInline
    inlines = [EmployeeProfileInline]


# Conditionally add EmployerInline outside the class
if apps.is_installed('employer'):
    from employer.models import Employer

    class EmployerInline(admin.StackedInline):
        model = Employer
        can_delete = False
        verbose_name_plural = 'employers'
        extra = 1

    # Add EmployerInline to the UserAdmin inlines
    UserAdmin.inlines.append(EmployerInline)


admin.site.register(PunchinUser, UserAdmin)
admin.site.register(TimeEntry)
