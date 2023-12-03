from django.shortcuts import render

# Create your views here.
from .models import TimeEntry

def list_time_entries(request):
    time_entries = TimeEntry.objects.all()
    return render(request, "core/list_time_entries.html", {"time_entries": time_entries})