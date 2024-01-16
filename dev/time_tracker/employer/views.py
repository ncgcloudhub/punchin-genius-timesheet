# employer/views.pymessages


# Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import ListView
from django.core.exceptions import ValidationError


# Local imports
from core.models import TimeEntry, EmployeeProfile, PunchinUser
# from core.forms import RegisterForm
from employer.models import Employer, Invitation, EmployerProfile
from .forms import TimeEntryForm, EmployerInvitationForm, EmployerRegistrationForm
from .tokens import employer_activation_token
from .utils import send_email, assign_employer_permissions
import logging


# Get the user model
User = get_user_model()

# Create a logger for logging error or information
logger = logging.getLogger(__name__)

# Login URL Constant
LOGIN_URL = 'login'

# Employer dashboard URL Constant
EMPLOYER_DASHBOARD_URL = 'employer_dashboard'


def is_superuser(user):
    return user.is_superuser


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
    print("User:", request.user)
    print("User has an employer profile.")
    employerprofile = getattr(request.user, 'employerprofile', None)
    print("Employer Profile:", employerprofile)
    if employerprofile is not None:
        employer = getattr(employerprofile, 'employer', None)
        print("Employer:", employer)
        if employer is not None:
            employees = EmployeeProfile.objects.filter(employer=employer)
            print("Employees:", employees)
            context = {
                'employees': employees,
                'employer_id': employer.id
            }
            return render(request, 'employer/employer_dashboard.html', context)
    return HttpResponse("Employer or Employer Profile not found.", status=404)


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


'''
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
                # Automatically associate the user with the employer
                employer = Employer.objects.get(user=request.user)
                request.user.employeeprofile.employer = employer
                request.user.employeeprofile.save()
                return handle_regular_user(request)
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
# @user_passes_test(can_access_employer_dashboard, login_url=LOGIN_URL)
# @permission_required('employer.can_view_employer_dashboard', raise_exception=True)
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
                # Automatically associate the user with the employer
                employer = Employer.objects.get(user=request.user)
                request.user.employeeprofile.employer = employer
                request.user.employeeprofile.save()
                return handle_regular_user(request)
        else:
            logger.info(
                "User is not a superuser and does not have an employeeprofile")
            # raise PermissionDenied("You are not allowed to view this page.")
    except PermissionDenied as e:
        # Log the exception
        logger.error("Permission denied: %s", e)
        # Handle the PermissionDenied exception, e.g., return an error page or redirect to a custom error page.
        return render(request, 'employer/access_denied.html')


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


def register_employer(request):
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']
            employer_name = form.cleaned_data['employer_name']
            if User.objects.filter(email__iexact=email).exists():
                messages.error(
                    request, 'An account with this email already exists.')
                logger.warning(
                    f"Attempt to register with existing email: {email}")
            else:
                try:
                    with transaction.atomic():
                        user = User.objects.create_user(
                            email=email, password=password, is_employer=True, is_active=False)
                        # Get the Employer instance and EmployerProfile
                        employer, employer_profile = form.save()
                        # The EmployerProfile is created in the form's save method
                        send_activation_email(user, employer_profile)
                        messages.success(
                            request, 'Registration successful! Please check your email to activate your account.')
                        return redirect('employer:account_activation_sent')
                except Exception as e:
                    logger.error(f"Unexpected error during registration: {e}")
                    messages.error(
                        request, 'An unexpected error occurred. Please try again.')
        else:
            logger.error(f"Form validation errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployerRegistrationForm()
    return render(request, 'employer/register_employer.html', {'form': form})


# commenting to test the employer profile creation.
'''
def register_employer(request):
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']
            employer_name = form.cleaned_data['employer_name']
            if User.objects.filter(email__iexact=email).exists():
                messages.error(
                    request, 'An account with this email already exists.')
                logger.warning(
                    f"Attempt to register with existing email: {email}")
            else:
                try:
                    with transaction.atomic():
                        user = User.objects.create_user(
                            email=email, password=password, is_employer=True, is_active=False)
                        # Get the Employer and EmployerProfile instances
                        employer, employer_profile = form.save()
                        send_activation_email(user, employer_profile)
                        messages.success(
                            request, 'Registration successful! Please check your email to activate your account.')
                        return redirect('employer:account_activation_sent')
                except Exception as e:
                    logger.error(f"Unexpected error during registration: {e}")
                    messages.error(
                        request, 'An unexpected error occurred. Please try again.')
        else:
            logger.error(f"Form validation errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployerRegistrationForm()
    return render(request, 'employer/register_employer.html', {'form': form})
'''


def account_activation_sent(request):
    return render(request, 'employer/account_activation_sent.html')


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


def send_email_with_template(user, subject, template_name, context, to_email):
    # Generate token with expiration
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Construct the activation link
    context['activation_link'] = f"{
        settings.MY_DOMAIN}/{template_name}/{uid}/{token}"

    # Define the email properties
    html_message = render_to_string(
        f'employer/email/{template_name}.html',
        context
    )
    recipient_list = [to_email]

    # Send the email using the utility function
    send_email(subject, '', recipient_list, html_message=html_message)

# Usage for sending invitation


def send_invitation(request):
    if request.method == 'POST':
        form = EmployerInvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.employer = request.user.employerprofile
            invitation.expiration_date = timezone.now() + timezone.timedelta(days=7)
            invitation.save()

            context = {
                'invitation': invitation,
            }
            send_email_with_template(
                request.user, 'You have been invited to join our platform', 'invitation_email', context, invitation.email)
            return redirect('employer:invitation_sent')

# Usage for sending activation email


def send_activation_email(employer):
    context = {
        'employer': employer,
    }
    send_email_with_template(employer.user, 'Activate Your Employer Account',
                             'account_activation_email', context, employer.employer_email_address)


def assign_employer_permissions(user):
    # Get the content type for the Employer model
    employer_content_type = ContentType.objects.get(
        app_label='employer', model='employer')

    # Get the permissions for the Employer model
    employer_permissions = Permission.objects.filter(
        content_type=employer_content_type)

    # Assign the permissions to the user
    for perm in employer_permissions:
        user.user_permissions.add(perm)
