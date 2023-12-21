# employer/views.py

from .utils import send_email_invitation  # Import the missing function
from django.urls import reverse
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from core.models import TimeEntry, EmployeeProfile  # Import from core.models
from .models import Employer, Invitation  # Import from employer.models
from core.forms import RegisterForm
from .forms import TimeEntryForm, EmployerInvitationForm, EmployerRegistrationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden

# Create your views here.


@login_required
def dashboard_redirect(request):
    if hasattr(request.user, 'employerprofile'):
        # URL name for employer's dashboard
        return redirect('employer_dashboard')
    else:
        return redirect('dashboard')  # URL name for employee's dashboard


@login_required
def employer_dashboard(request):
    if not hasattr(request.user, 'employer'):
        return HttpResponseForbidden("You are not allowed to view this page.")
    return render(request, 'employer/employer_dashboard.html')


@login_required
def employer_registration(request):
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            employer = form.save(commit=False)
            employer.save()
            return redirect('employer:employer_dashboard')
    else:
        form = EmployerRegistrationForm()
    return render(request, 'employer/employer_registration.html', {'form': form})


@login_required
def send_invitation(request):
    if request.method == 'POST':
        form = EmployerInvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.employer = request.user.employer
            invitation.expiration_date = timezone.now() + timezone.timedelta(days=7)
            invitation.save()
            send_email_invitation(request, invitation)  # Call the function
            return redirect('employer:invitation_sent')
    else:
        form = EmployerInvitationForm()
    return render(request, 'employer/invitation_form.html', {'form': form})


def accept_invitation(request, token):
    invitation = get_object_or_404(Invitation, token=token, is_accepted=False)
    if invitation.expiration_date >= timezone.now():
        user = request.user
        user.employer = invitation.employer
        user.save()
        invitation.is_accepted = True
        invitation.save()
        return HttpResponse('Invitation accepted.')
    else:
        return HttpResponse('Invitation has expired.', status=410)


def invitation_sent(request):
    return render(request, 'employer/invitation_sent.html')
