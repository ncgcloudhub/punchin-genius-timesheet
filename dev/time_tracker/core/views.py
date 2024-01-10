# core/views.py --> app specific views

from django.apps import apps
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, get_user_model, authenticate
from .models import TimeEntry, EmployeeProfile
from .forms import TimeEntryForm, RegisterForm
from django.db.models import Sum, Avg
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
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
from .forms import EmployeeLinkForm
from django.contrib.auth.models import Group


# Conditional import
if apps.is_installed('employer'):
    from employer.models import Employer
    from employer.models import EmployerProfile
    # Other necessary imports from the employer app
else:
    Employer = None  # Or some other fallback handling

# Configure a logger for your application
logger = logging.getLogger(__name__)

# Create your views here.
User = get_user_model()


def can_access_employee_dashboard(user):
    return user.is_superuser or (user.is_authenticated and not user.is_employer)


# checks whether the user is authenticated and is either a superuser (is_superuser) or has the is_employer attribute set to True.


def can_access_employer_dashboard(user):
    return user.is_authenticated and (user.is_superuser or user.is_employer)


def account_activation_sent(request):
    # Render a template that informs the user that an activation email has been sent
    return render(request, 'core/account_activation_sent.html')


def register(request):      # Registration view
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
                    activation_link = f"{settings.MY_DOMAIN}{
                        reverse('activate', args=[uid, token])}"

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


def activate(request, uidb64, token):
    # Account Activation View (Create a view to handle the link that the user clicks from their email.
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
        return render(request, 'core/account_activation_invalid.html')


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


class CustomLogoutView(LogoutView):
    template_name = 'core/logout.html'
    next_page = reverse_lazy('login')  # Where to redirect after logout

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'post':
            # Clear all previous messages
            storage = messages.get_messages(request)
            for message in storage:
                # This will remove the message from the queue
                pass
            storage.used = True

            logout(request)
            messages.success(request, "You have successfully logged out.")
            return redirect(self.next_page)
        else:
            return super().dispatch(request, *args, **kwargs)

# Employee dashboard view in core/views.py
# checks whether the user is authenticated and is either a superuser (is_superuser) or has the is_employee attribute set to True.


@login_required
def employee_dashboard(request):
    print("Is the user authenticated?", request.user.is_authenticated)
    context = {
        'now': timezone.now(),
        'is_employer': request.user.is_employer,
        'associated_with_employer': hasattr(request.user, 'employeeprofile') and request.user.employeeprofile.employer is not None,
        'can_apply_for_employer': not request.user.is_employer and not hasattr(request.user, 'employeeprofile'),
    }
    # Check if the user is a superuser
    if request.user.is_superuser:
        # If the user is a superuser, get the count of all employers
        employer_count = Employer.objects.count()
        # Add employer_count to the context
        context['employer_count'] = employer_count

    return render(request, 'core/employee_dashboard.html', context)


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
@transaction.atomic
def apply_employer(request):
    # Check if the user is already an employer or associated with an employer
    if request.user.is_employer or (hasattr(request.user, 'employeeprofile') and request.user.employeeprofile.employer):
        messages.info(
            request, "You are already an employer or associated with an employer.")
        return redirect('core:employee_dashboard')

    if request.method == 'POST':
        # When the form is submitted, make the user an employer and admin for the employer account
        request.user.is_employer = True
        request.user.save()
        # Make the user a staff member and potentially part of the admin group
        request.user.is_staff = True
        admin_group, _ = Group.objects.get_or_create(name='EmployerAdmins')
        request.user.groups.add(admin_group)
        request.user.save()

        # Create an EmployerProfile for this user if it doesn't exist
        employer_profile, created = EmployerProfile.objects.get_or_create(
            user=request.user)
        if created:
            # Optionally set additional fields on employer_profile
            employer_profile.save()

        messages.success(
            request, "You have successfully applied to be an employer and are now the admin of the employer account.")
        # Redirect to a page where the user can complete their employer profile details
        return redirect('employer:register_employer_details')
    else:
        # If the method is GET, show a confirmation page to apply as an employer
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
    if request.method == 'POST':
        # Ensure the user has an employer profile
        try:
            employee_profile = request.user.employeeprofile
            if not employee_profile.employer:
                messages.error(
                    request, "You must be associated with an employer to clock in.")
                # Redirect to profile edit or association view
                return redirect('core:profile_edit')

            # Create a new TimeEntry for the user
            TimeEntry.objects.create(
                user=request.user, clock_in=timezone.now())
            messages.success(request, "Clocked in successfully.")
            # Redirect to the employee dashboard
            return redirect('core:employee_dashboard')

        except EmployeeProfile.DoesNotExist:
            messages.error(
                request, "Your employee profile is not set up. Please complete your profile.")
            # Redirect to profile setup view
            return redirect('core:profile_setup')

    else:
        # If not a POST request, show the clock-in page (or redirect as appropriate)
        return render(request, 'core/clock_in.html')


@login_required
def clock_out(request):
    if request.method == 'POST':
        # Fetch the latest unclosed TimeEntry
        try:
            latest_entry = TimeEntry.objects.filter(
                user=request.user, clock_out__isnull=True).latest('clock_in')
            latest_entry.clock_out = timezone.now()  # Record the clock out time
            latest_entry.save()
            messages.success(request, "Clocked out successfully.")
            # Redirect to the employee dashboard
            return redirect('core:employee_dashboard')

        except TimeEntry.DoesNotExist:
            messages.error(
                request, "No ongoing time entry found to clock out from.")
            return redirect('core:clock_in')  # Redirect to clock in
    else:
        # If not a POST request, show the clock-out page (or redirect as appropriate)
        return render(request, 'core/clock_out.html')


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
def user_profile_settings(request):
    # Assuming 'phone_number' is a field in the EmployeeProfile model
    profile = EmployeeProfile.objects.get(user=request.user)

    if request.method == "POST":
        # Update user's personal information
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        profile.phone_number = request.POST.get(
            'phone_number', profile.phone_number)
        user.save()
        profile.save()
        messages.success(request, "Your profile has been updated.")
        return redirect('core:user_profile_settings')
    else:
        # Pass the current values to the template to populate the form fields
        context = {
            'user': request.user,
            'profile': profile
        }
        return render(request, 'core/user_profile_settings.html', context)


@login_required
def user_app_settings(request):
    # Your logic for handling app specific user settings
    return render(request, 'user_app_settings.html', context)


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
