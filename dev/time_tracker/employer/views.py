# employer/views.py


from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model  # Import get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from .utils import send_email  # Import the missing function
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
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.views.generic import ListView
from django.conf import settings
from django.utils.encoding import force_str
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from .tokens import employer_activation_token
from django.shortcuts import get_object_or_404


import logging

# Get the user model
User = get_user_model()

# Create a logger for logging error or information
logger = logging.getLogger(__name__)

# Login URL Constant
LOGIN_URL = 'login'

# Employer dashboard URL Constant
EMPLOYER_DASHBOARD_URL = 'employer_dashboard'


def get_first_user():
    return User.objects.first()


@login_required
# Dashboard redirect function
def dashboard_redirect(request):
    if hasattr(request.user, 'employerprofile'):
        # URL name for employer's dashboard
        return redirect('employer:employer_dashboard')
    else:
        # URL name for employee's dashboard
        return redirect('core:employee_dashboard')

# Now generate the token
# Utility Functions


def generate_token_for_user(user):
    if user is not None:
        return employer_activation_token.make_token(user)
    else:
        logger.error("User object is None when generating token")
        return None


def get_uid_for_user(user):
    if user is not None:
        return urlsafe_base64_encode(force_bytes(user.pk))
    else:
        return None


# checks whether the user is authenticated and is either a superuser (is_superuser) or has the is_employer attribute set to True.


def can_access_employer_dashboard(user):
    return user.is_authenticated and (user.is_superuser or user.is_employer)


def handle_superuser(request):
    # Superuser logic here
    print("Superuser bypassing employer profile check.")
    # Retrieve all employers
    employers = Employer.objects.all()
    # Get the count of employers
    employer_count = employers.count()
    # Pass both employers and employer_count to your template
    context = {'employers': employers, 'employer_count': employer_count}
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


def is_superuser(user):
    return user.is_superuser


@user_passes_test(is_superuser, login_url='login')
def employer_list(request):
    employers = Employer.objects.all()
    return render(request, 'employer/employer_list.html', {'employers': employers})


class EmployerListView(ListView):
    model = Employer
    template_name = 'employer/employer_list.html'  # your template name
    context_object_name = 'employers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)  # print the context to the console
        return context


@login_required
@user_passes_test(can_access_employer_dashboard, login_url=LOGIN_URL)
@permission_required('employer.can_view_employer_dashboard', raise_exception=True)
def employer_dashboard(request):
    try:
        if request.user.is_superuser:
            logger.info("User is a superuser")
            return handle_superuser(request)
        elif hasattr(request.user, 'employeeprofile'):
            if request.user.employeeprofile.employer is not None:
                logger.info(
                    "User has an employeeprofile associated with an employer")
                return handle_regular_user(request)
            else:
                logger.info(
                    "User has an employeeprofile but it is not associated with an employer")
        else:
            logger.info(
                "User is not a superuser and does not have an employeeprofile")
            raise PermissionDenied("You are not allowed to view this page.")
    except PermissionDenied as e:
        # Log the exception
        logger.error("Permission denied: %s", e)
        # Handle the PermissionDenied exception, e.g., return an error page or redirect to a custom error page.
        return render(request, 'employer/access_denied.html')


'''
@login_required
@user_passes_test(can_access_employer_dashboard, login_url=LOGIN_URL)
@permission_required('employer.can_view_employer_dashboard', raise_exception=True)
def employer_dashboard(request):
    try:
        if request.user.is_superuser:
            return handle_superuser(request)
        elif hasattr(request.user, 'employeeprofile') and request.user.employeeprofile.employer is not None:
            return handle_regular_user(request)
        else:
            raise PermissionDenied("You are not allowed to view this page.")
    except PermissionDenied as e:
        # Handle the PermissionDenied exception, e.g., return an error page or redirect to a custom error page.
        return render(request, 'employer/access_denied.html')
'''


def accept_invitation(request, token):
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to accept the invitation.")
        return redirect(f"{reverse('login')}?next={request.path}")

    invitation = get_object_or_404(Invitation, token=token, is_accepted=False)
    if invitation.expiration_date >= timezone.now():
        if invitation.employer.is_activated:  # Make sure employer is activated
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
            return HttpResponse('Employer is not activated.', status=403)
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
                user.is_staff = True  # If you want the employer to also be a staff member
                user.save()
                # Give the user permission to view the employer dashboard
                permission = Permission.objects.get(
                    codename='can_view_employer_dashboard')
                user.user_permissions.add(permission)
                login(request, user,
                      backend='django.contrib.auth.backends.ModelBackend')
                return redirect('employer:register_employer_details')
    else:
        user_form = RegisterForm()
    return render(request, 'core/register.html', {'form': user_form})


# @login_required
def register_employer_details(request):
    if request.method == 'POST':
        employer_form = EmployerRegistrationForm(request.POST)
        if employer_form.is_valid():
            employer = employer_form.save(commit=False)
            employer.user = request.user
            employer.user.save()  # Save the user instance
            employer.save()  # Now you can save the employer instance
            send_activation_email(employer)  # Send the activation email
            messages.success(
                request, 'Registration successful! Please check your email to activate your account.')
            return redirect('employer:account_activation_sent')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        employer_form = EmployerRegistrationForm()

    return render(request, 'employer/register_employer_details.html', {'form': employer_form})


def account_activation_sent(request):
    return render(request, 'employer/account_activation_sent.html')


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


def activate_employer(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and employer_activation_token.check_token(user, token):
        user.is_active = True
        user.is_employer = True  # Set user as employer here
        user.is_staff = True  # Set user as staff here
        # Assuming you have an `activated` field in your `EmployerProfile` model
        # user.employerprofile.activated = True
        user.save()
        login(request, user)

        employer_profile, created = EmployerProfile.objects.get_or_create(
            user=user)
        employer_profile.activated = True  # Activate the profile
        employer_profile.save()

        # Assign employer-specific permissions here
        assign_employer_permissions(user)

        # Redirect to the employer dashboard
        return redirect('employer:employer_dashboard')
    else:
        # Render a page to inform the employer that the activation link is invalid
        return render(request, 'employer/account_activation_invalid.html')


def send_email_invitation(invitation):
    # Define the email properties
    subject = 'You have been invited to join our platform'
    message = f'Hi, you have been invited to join our platform. Please use this invitation: {
        invitation}'
    recipient_list = [invitation.email]  # Replace with the employee's email

    # Send the email using the utility function
    send_email(subject, message, recipient_list)


# This function sends an invitation email to a potential employee.
def send_invitation(request):
    if request.method == 'POST':
        form = EmployerInvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.employer = request.user.employerprofile
            invitation.expiration_date = timezone.now() + timezone.timedelta(days=7)
            invitation.save()

            invitation_link = f"{settings.MY_DOMAIN}{
                reverse('employer:accept_invitation', args=[invitation.token])}"

            subject = 'You have been invited to join our platform'
            html_message = render_to_string('employer/email/invitation_email.html', {
                'invitation': invitation,
                'invitation_link': invitation_link
            })
            recipient_list = [invitation.email]

            send_email(subject, '', recipient_list, html_message=html_message)
            return redirect('employer:invitation_sent')
    else:
        form = EmployerInvitationForm()
    return render(request, 'employer/send_invitation.html', {'form': form})


# Sending the activation email to employer email address after employer account registration completed.
def send_activation_email(employer):
    # Generate token with expiration
    token = employer_activation_token.make_token(employer.user)
    uid = urlsafe_base64_encode(force_bytes(employer.user.pk))

    # Construct the activation link
    activation_link = f"{settings.MY_DOMAIN}/employer/activate/{uid}/{token}"

    # Define the email properties
    subject = 'Activate Your Employer Account'
    html_message = render_to_string(
        'employer/account_activation_email.html',
        {
            'employer': employer,
            'activation_link': activation_link
        }
    )
    recipient_list = [employer.employer_email_address]

    # Send the email using the utility function
    send_email(subject, '', recipient_list, html_message=html_message)
