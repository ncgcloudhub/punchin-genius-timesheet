# /core/admin.py

from django.contrib import admin
from .models import PunchinUser, TimeEntry

# Register your models here.


admin.site.register(PunchinUser)  # using  custom user model.
admin.site.register(TimeEntry)
