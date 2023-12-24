# employer/views.py

from .utils import send_email_invitation  # Import the missing function
from django.urls import reverse
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from core.models import TimeEntry, EmployeeProfile  # Import from core.models
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
from core.models import PunchinUser
from core.forms import RegisterForm


# Create your views here.


@login_required
def dashboard_redirect(request):
    if hasattr(request.user, 'employerprofile'):
        # URL name for employer's dashboard
        return redirect('employer:employer_dashboard')
    else:
        return redirect('core:dashboard')  # URL name for employee's dashboard

# checks whether the user is authenticated and is either a superuser (is_superuser) or has the is_employer attribute set to True.


def can_access_employer_dashboard(user):
    return user.is_authenticated and (user.is_superuser or user.is_employer)


@login_required
@user_passes_test(can_access_employer_dashboard, login_url='employer_dashboard')
@permission_required('employer.can_view_employer_dashboard', raise_exception=True)
def employer_dashboard(request):
    # Allow superusers to access the dashboard without an employer profile.
    if request.user.is_superuser:
        print("Superuser bypassing employer profile check.")
        # You might want to retrieve all employers or perform some other logic for superusers.
        # For example, let's assume you just list all employers.
        employers = Employer.objects.all()
        context = {'employers': employers}
        return render(request, 'employer/employer_dashboard.html', context)

    # For regular users, check if they have an employer profile.
    elif hasattr(request.user, 'employerprofile'):
        print("User has an employer profile.")
        employer_id = request.user.employerprofile.employer_id
        employees = request.user.employerprofile.employee_set.all()
        context = {
            'employees': employees,
            'employer_id': employer_id
        }
        return render(request, 'employer/employer_dashboard.html', context)
    else:
        print("User does not have an employer profile.")
        return HttpResponseForbidden("You are not allowed to view this page.")


'''
def employer_registration(request):
    if request.method == 'POST':
        user_form = RegisterForm(request.POST)
        employer_form = EmployerRegistrationForm(request.POST)
        if user_form.is_valid() and employer_form.is_valid():
            # Create a new user and set them as an employer
            user = user_form.save(commit=False)
            user.is_employer = True
            user.set_password(user_form.cleaned_data['password1'])
            # Using email as username if applicable
            user.username = user_form.cleaned_data['email']
            user.save()

            # Create a new employer profile
            employer = employer_form.save(commit=False)
            employer.user = user
            # Set additional fields if they are not already handled by the form
            employer.name = employer_form.cleaned_data['employer_name']
            employer.address = employer_form.cleaned_data['employer_address']
            employer.city = employer_form.cleaned_data['employer_city']
            employer.state = employer_form.cleaned_data['employer_state']
            employer.zip_code = employer_form.cleaned_data['employer_zip']
            employer.ein_number = employer_form.cleaned_data['employer_ein']
            # Ensure this is the field name on your model
            employer.email_address = user.email
            # Add any additional fields you need
            employer.save()

            # Send an email confirmation to the employer's email address
            send_mail(
                'Welcome to PunchIn Genius Timesheet!',
                'Your employer account has been successfully created.',
                'no-reply@punchingenius.com',
                [user.email],
                fail_silently=False,
            )

            # Log in the user automatically after registering (optional)
            login(request, user)

            # Redirect to the employer's dashboard
            return redirect('employer:employer_dashboard')
        else:
            # If the form is not valid, render the registration page again with form errors
            return render(request, 'employer/employer_registration.html', {
                'user_form': user_form,
                'employer_form': employer_form
            })
    else:
        # If it's a GET request, render the empty registration form
        user_form = RegisterForm()
        employer_form = EmployerRegistrationForm()

    return render(request, 'employer/employer_registration.html', {
        'user_form': user_form,
        'employer_form': employer_form
    })
'''


@login_required
def send_invitation(request):
    if not request.user.is_employer:  # Assuming you have a method/property to check if the user is an employer
        return HttpResponseForbidden("You are not allowed to perform this action. Please select the 'Employee' option in the registration form.")

    if request.method == 'POST':
        form = EmployerInvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            # Assuming you have a ForeignKey to the employer in the user profile
            invitation.employer = request.user.employerprofile
            invitation.expiration_date = timezone.now() + timezone.timedelta(days=7)
            invitation.save()
            # Send the email invitation logic goes here
            send_email_invitation(request, invitation)  # Call the function
            return redirect('invitation_sent')
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


# @login_required
def register_employer_details(request):
    # Retrieve user data from the session
    user_data = request.session.get('user_data', None)

    if not user_data:
        return redirect('employer:register_user')

    if request.method == 'POST':
        employer_form = EmployerRegistrationForm(request.POST)

        if employer_form.is_valid():
            # Save employer details
            employer_data = employer_form.cleaned_data

            # Store employer data in the session
            request.session['employer_data'] = employer_data

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
