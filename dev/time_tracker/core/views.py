# core/views.py

from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, get_user_model, authenticate
from .models import TimeEntry, EmployeeProfile
from .forms import TimeEntryForm, RegisterForm
from django.db.models import Sum, Avg
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from .utils import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.template.loader import render_to_string
# Import the can_access_employer_dashboard function from the appropriate location
from core.utils import can_access_employer_dashboard
import logging
from django.db import transaction
from django.core.mail import EmailMessage, BadHeaderError


# Configure a logger for your application
logger = logging.getLogger(__name__)

# Create your views here.
User = get_user_model()


def can_access_employee_dashboard(user):
    return user.is_superuser or (user.is_authenticated and user.is_employer)


# checks whether the user is authenticated and is either a superuser (is_superuser) or has the is_employer attribute set to True.


def can_access_employer_dashboard(user):
    return user.is_authenticated and (user.is_superuser or user.is_employer)


def account_activation_sent(request):
    # Render a template that informs the user that an activation email has been sent
    return render(request, 'core/account_activation_sent.html')

# Registration view


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                try:
                    user = form.save(commit=False)
                    user.is_active = False  # User will be inactive until they activate via email
                    user.is_employer = False  # Default as employee
                    # Add this line to save the first name
                    user.first_name = form.cleaned_data.get('first_name')
                    # Add this line to save the last name
                    user.last_name = form.cleaned_data.get('last_name')
                    user.save()

                    # Construct activation link
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = account_activation_token.make_token(user)
                    activation_link = f"{settings.MY_DOMAIN}{reverse('activate', args=[uid, token])}"
                    activation_link = f"{settings.MY_DOMAIN}{reverse('activate', args=[uid, token])}"

                    # Prepare the email message using render_to_string
                    message = render_to_string('core/account_activation_email.html', {
                        'user': user,
                        'activation_link': activation_link,
                    })

                    # Create the email and set content to HTML
                    email = EmailMessage(
                        'Activate Your PunchIn Account',  # Email subject
                        message,  # Email body (HTML content)
                        settings.DEFAULT_FROM_EMAIL,  # From email
                        [user.email]  # To email
                    )
                    email.content_subtype = 'html'  # Specify the subtype as HTML

                    # Send the email
                    try:
                        email.send()
                    except BadHeaderError:
                        # If there is a bad header error, handle it
                        return HttpResponse('Invalid header found.')

                    # Redirect to the account activation sent page
                    return redirect('account_activation_sent')

                except Exception as e:
                    # Log the error
                    logger.error(
                        f"Error during registration for {user.email}: {e}")
                    # Rollback the user creation
                    raise

                    # Optional: Add a message for the end user
                    messages.error(
                        request, "An error occurred during registration. Please try again.")

    else:
        form = RegisterForm()

    return render(request, 'core/register.html', {'form': form})

# Account Activation View (Create a view to handle the link that the user clicks from their email.)


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('core:employee_dashboard')
    else:
        return render(request, 'account_activation_invalid.html')


# checks whether the user is authenticated and is either a superuser (is_superuser) or has the is_employee attribute set to True.


# Employee dashboard view in core/views.py
@login_required
@user_passes_test(can_access_employee_dashboard, login_url='employee_dashboard')
def employee_dashboard(request):
    # Print out to the console for debugging
    print("Is the user authenticated?", request.user.is_authenticated)
    # Include any logic you want specifically for the employee dashboard
    return render(request, 'core/employee_dashboard.html', {'now': timezone.now()})


@login_required
# Your logic to determine the redirection URL goes here
# For example, you can check the user's role and redirect accordingly
def dashboard_redirect(request):
    if hasattr(request.user, 'employerprofile'):
        return redirect('employer:employer_dashboard')
    else:
        return redirect('core:employee_dashboard')
        # Handle login failure logic...


@login_required
# Providing a Path to Become an Employer
def apply_employer(request):
    if request.method == 'POST':
        # Handle the form submission and set user as an employer
        request.user.is_employer = True
        request.user.save()
        # Redirect to employer-specific setup or dashboard
        # make sure to define this view and URL
        return redirect('employer_dashboard')
    else:
        # Show a confirmation or information page about becoming an employer
        # create this template
        return render(request, 'core/apply_employer.html')


@login_required
def join_employer(request):
    if request.method == 'POST':
        form = EmployeeLinkForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['invitation_token']
            try:
                invitation = Invitation.objects.get(
                    token=token, is_accepted=False)
                # Assuming EmployeeProfile and Invitation have the necessary fields
                employee_profile, created = EmployeeProfile.objects.get_or_create(
                    user=request.user)
                employee_profile.employer = invitation.employer
                employee_profile.save()
                invitation.is_accepted = True
                invitation.save()
                messages.success(request, "Successfully joined the employer.")
                return redirect('core:employee_dashboard')
            except Invitation.DoesNotExist:
                messages.error(request, "Invalid or expired invitation.")
    else:
        form = EmployeeLinkForm()

    return render(request, 'core/join_employer.html', {'form': form})


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


@login_required
def clock_in_view(request):
    # Your logic here
    return render(request, 'core/clock_in.html')


@login_required
def clock_out_view(request):
    # Your logic here
    return render(request, 'core/clock_out.html')


<<<<<<< HEAD
class CustomLoginView(LoginView):
    template_name = 'core/login.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the current date
        context['current_date'] = timezone.now()
        return context

    def get_success_url(self):
        # Check if the user has an employer profile and is marked as an employer
        if hasattr(self.request.user, 'employerprofile') and self.request.user.is_employer:
            return reverse('employer:employer_dashboard')
        else:
            # Redirect to employee dashboard for all other users
            return reverse('core:employee_dashboard')


@login_required
# Accepting Invitation View: Create a view where employees can enter the invitation code or token to link themselves to the employer
def accept_invitation(request):
    if request.method == 'POST':
        # Form where they input the invitation token
        form = EmployeeLinkForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['invitation_token']
            try:
                invitation = Invitation.objects.get(
                    token=token, is_accepted=False)
                employee_profile = request.user.employeeprofile
                employee_profile.employer = invitation.employer
                employee_profile.save()
                invitation.is_accepted = True
                invitation.save()
                # Redirect to a confirmation or the employee dashboard
                return redirect('core:employee_dashboard')
            except Invitation.DoesNotExist:
                # Handle invalid or used invitation token
                pass
    else:
        form = EmployeeLinkForm()
    return render(request, 'core/accept_invitation.html', {'form': form})
=======
def custom_login(request):
    # Existing login logic here...
    if request.user.is_authenticated:
        if hasattr(request.user, 'employerprofile'):
            return redirect('employer_dashboard')
        else:
            return redirect('employee_dashboard')
    # Handle login failure logic...


@login_required
def dashboard_redirect(request):
    if hasattr(request.user, 'employerprofile'):
        return redirect('employer:employer_dashboard')
    else:
        # Make sure to define this view and URL
        return redirect('employee_dashboard')
>>>>>>> 626ab05b3eeef995d737e5d886b205d7fb0e9860
