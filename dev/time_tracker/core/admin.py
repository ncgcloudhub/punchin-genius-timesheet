from django.contrib import admin

# Register your models here.
from .models import User, TimeEntry

admin.site.register(User)
admin.site.register(TimeEntry)
