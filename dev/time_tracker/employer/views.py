# employer/views.py

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
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
        return redirect('employer:employer_dashboard')
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
    return render(request, 'employer/send_invitation.html', {'form': form})


def accept_invitation(request, token):
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to accept the invitation.")
        return redirect(f"{reverse('login')}?next={request.path}")

    invitation = get_object_or_404(Invitation, token=token, is_accepted=False)
    if invitation.expiration_date >= timezone.now():
        user = request.user
        employee_profile, created = EmployeeProfile.objects.get_or_create(
            user=user)
        employee_profile.employer = invitation.employer
        employee_profile.save()
        invitation.is_accepted = True
        invitation.save()
        # Send confirmation email here (use Django's send_mail function)
        return HttpResponse('Invitation accepted.')
    else:
        return HttpResponse('Invitation has expired.', status=410)


def invitation_sent(request):
    return render(request, 'employer/invitation_sent.html')


def register_user(request):
    if request.method == 'POST':
        user_form = RegisterForm(request.POST)
        if user_form.is_valid():
            with transaction.atomic():
                user = user_form.save(commit=False)
                user.is_employer = True
                user.save()
                login(request, user,
                      backend='django.contrib.auth.backends.ModelBackend')
                return redirect('employer:register_employer_details')
    else:
        user_form = RegisterForm()

    return render(request, 'employer/register_user.html', {'form': user_form})


@login_required
def register_employer_details(request):
    # Initialize the form
    if request.method == 'POST':
        employer_form = EmployerRegistrationForm(request.POST)

        if employer_form.is_valid():
            # Create but don't commit the save yet
            employer = employer_form.save(commit=False)
            employer.user = request.user  # Associate the user

            # You can use session to temporarily store the employer details for confirmation
            employer_data = employer_form.cleaned_data
            # Store data in session for confirmation or further processing
            request.session['employer_data'] = employer_data

            # You might want to add additional steps here before saving the employer, such as a confirmation page
            # For now, let's save the employer and redirect to a confirmation or directly to the dashboard
            employer.save()
            request.user.is_employer = True  # Mark the user as an employer
            request.user.save()

            # Redirect to a confirmation page or employer dashboard
            # Redirect to the confirmation page or another page for the next step
            return redirect('employer:confirm_registration')
    else:
        employer_form = EmployerRegistrationForm()

    return render(request, 'employer/register_employer_details.html', {'employer_form': employer_form})


@login_required
def confirm_registration(request):
    # Retrieve user and employer data from the session
    user_data = request.session.get('user_data', None)
    employer_data = request.session.get('employer_data', None)

    if not user_data or not employer_data:
        return redirect('employer:register_user')

    # Render a confirmation page displaying user and employer data
    return render(request, 'employer/confirm_registration.html', {
        'user_data': user_data,
        'employer_data': employer_data
    })
