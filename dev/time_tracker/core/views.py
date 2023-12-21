# core/views.py

from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, get_user_model
from .models import TimeEntry, EmployeeProfile
from .forms import TimeEntryForm, RegisterForm
from django.db.models import Sum, Avg
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Create your views here.
User = get_user_model()


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Include the 'core' namespace
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})


@login_required
def dashboard(request):
    # Print out to the console for debugging
    print("Is the user authenticated?", request.user.is_authenticated)

    # Continue with your existing logic...
    return render(request, 'core/dashboard.html', {'now': timezone.now()})


@login_required
def list_time_entries(request):
    entries = TimeEntry.objects.filter(user=request.user)
    return render(request, "core/list_time_entries.html", {"entries": entries})


@login_required
def clock_in(request):
    return HttpResponse("Clock in page")


@login_required
def clock_out(request):
    return HttpResponse("Clock out page")


@login_required
def create_time_entry(request):
    if request.method == "POST":
        form = TimeEntryForm(request.POST)
        if form.is_valid():
            time_entry = form.save(commit=False)
            time_entry.user = request.user
            time_entry.save()
            return redirect('list-entries')
    else:
        form = TimeEntryForm()
    return render(request, "core/time_entry_form.html", {"form": form})


@login_required
def user_profile(request):
    return render(request, "core/user_profile.html", {"user": request.user})


@login_required
def generate_report(request):
    total_hours = TimeEntry.objects.aggregate(Sum('duration'))
    average_hours = TimeEntry.objects.aggregate(Avg('duration'))
    return render(request, 'core/report.html', {'total_hours': total_hours, 'average_hours': average_hours})


def login_redirect(request):
    return redirect('/accounts/login/')


@login_required
def dashboard_view(request):
    # Your logic here
    return render(request, 'core/dashboard.html')


@login_required
def clock_in_view(request):
    # Your logic here
    return render(request, 'core/clock_in.html')


@login_required
def clock_out_view(request):
    # Your logic here
    return render(request, 'core/clock_out.html')
