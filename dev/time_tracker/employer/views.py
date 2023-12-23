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
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import get_user_model
from core.forms import RegisterForm


# Create your views here.


@login_required
def dashboard_redirect(request):
    if hasattr(request.user, 'employerprofile'):
        # URL name for employer's dashboard
        return redirect('employer:employer_dashboard')
    else:
        return redirect('core:dashboard')  # URL name for employee's dashboard


@login_required
@permission_required('employer.can_view_employer_dashboard', raise_exception=True)
def employer_dashboard(request):
    print(request.user)
    if not hasattr(request.user, 'employerprofile'):
        print("User does not have an employer profile.")
        return HttpResponseForbidden("You are not allowed to view this page.")

    # Assuming 'employerprofile' is a related name for the Employer model linked to the User.
    print("User has an employer profile.")
    employer_id = request.user.employerprofile.employer_id
    employees = request.user.employerprofile.employee_set.all()
    # Include 'employer_id' in the context dictionary.
    context = {
        'employees': employees,
        'employer_id': employer_id  # Add this line
    }
    # return render(request, 'employer/employer_dashboard.html')
    return render(request, 'employer/employer_dashboard.html', context)


def employer_registration(request):
    if request.method == 'POST':
        user_form = RegisterForm(request.POST)
        employer_form = EmployerRegistrationForm(request.POST)
        if user_form.is_valid() and employer_form.is_valid():
            user = user_form.save(commit=False)
            user.is_employer = True  # This field should be added to your user model
            # Set the password for the user
            user.set_password(user_form.cleaned_data['password1'])
            user.save()

            employer = employer_form.save(commit=False)
            employer.user = user  # Link the employer instance to the user
            # Set the employer email to the user's email
            employer.employer_email_address = user.email
            employer.save()

            return redirect('employer:employer_dashboard')
    else:
        user_form = RegisterForm()
        employer_form = EmployerRegistrationForm()

    return render(request, 'employer/employer_registration.html', {'user_form': user_form, 'employer_form': employer_form})


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
