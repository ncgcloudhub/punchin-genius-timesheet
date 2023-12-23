# /core/admin.py

from .models import EmployeeProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from .models import PunchinUser, TimeEntry
from employer.models import Employer


# Inline definition
class EmployerInline(admin.StackedInline):
    model = Employer
    can_delete = False
    verbose_name_plural = 'employers'
    extra = 1

# Parent model admin


class UserAdmin(admin.ModelAdmin):
    inlines = (EmployerInline, )


# Register your models here.
admin.site.register(PunchinUser, UserAdmin)
admin.site.register(TimeEntry)
