# employer/views.py

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from .utils import send_email_invitation  # Import the missing function
from django.urls import reverse
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from core.models import TimeEntry, EmployeeProfile, PunchinUser
# from .models import Employer, Invitation  # Import from employer.models
# Import EmployerProfile from employer.models
from employer.models import Employer, Invitation, EmployerProfile
from core.forms import RegisterForm
from .forms import TimeEntryForm, EmployerInvitationForm, EmployerRegistrationForm
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.db import transaction
from django.conf import settings

# Create your views here.


@login_required
def dashboard_redirect(request):
    if hasattr(request.user, 'employerprofile'):
        # URL name for employer's dashboard
        return redirect('employer:employer_dashboard')
    else:
        # URL name for employee's dashboard
        return redirect('core:employee_dashboard')

# checks whether the user is authenticated and is either a superuser (is_superuser) or has the is_employer attribute set to True.


def can_access_employer_dashboard(user):
    return user.is_authenticated and (user.is_superuser or user.is_employer)


# Constants for URLs
LOGIN_URL = 'login'  # URL of the login page
EMPLOYER_DASHBOARD_URL = 'employer_dashboard'  # URL of the employer dashboard


def handle_superuser(request):
    # Superuser logic here
    print("Superuser bypassing employer profile check.")
    # You might want to retrieve all employers or perform some other logic for superusers.
    # For example, let's assume you just list all employers.
    employers = Employer.objects.all()
    context = {'employers': employers}
    return render(request, 'employer/employer_dashboard.html', context)


def handle_regular_user(request):
    # Regular user with employer profile logic here
    print("User has an employer profile.")
    employer_id = request.user.employerprofile.employer_id
    employees = request.user.employerprofile.employee_set.all()
    context = {
        'employees': employees,
        'employer_id': employer_id
    }
    return render(request, 'employer/employer_dashboard.html', context)


@login_required
@user_passes_test(can_access_employer_dashboard, login_url=LOGIN_URL)
@permission_required('employer.can_view_employer_dashboard', raise_exception=True)
def employer_dashboard(request):
    try:
        if request.user.is_superuser:
            return handle_superuser(request)
        elif hasattr(request.user, 'employerprofile'):
            return handle_regular_user(request)
        else:
            raise PermissionDenied("You are not allowed to view this page.")
    except PermissionDenied as e:
        # Handle the PermissionDenied exception, e.g., return an error page or redirect to a custom error page.
        return render(request, 'access_denied.html')


@login_required
def send_invitation(request):
    if not request.user.is_employer:
        return HttpResponseForbidden("You are not allowed to perform this action.")

    if request.method == 'POST':
        form = EmployerInvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.employer = request.user.employerprofile
            invitation.expiration_date = timezone.now() + timezone.timedelta(days=7)
            invitation.save()

            # Construct invitation link
            invitation_link = f"{settings.MY_DOMAIN}{reverse('employer:accept_invitation', args=[invitation.token])}"

            # Send the email invitation logic
            # Update your function to accept the link
            send_email_invitation(invitation, invitation_link)

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
