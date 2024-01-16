# /employer/models.py


import random
import uuid
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.conf import settings
from django import forms
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
# from core.models import EmployeeProfile
from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.db import models
from django.conf import settings

import logging


logger = logging.getLogger(__name__)


def generate_employer_id():
    # Generates a unique random 10-digit number as a string
    # Ensures uniqueness in the unlikely event of a collision
    while True:
        employer_id = str(random.randint(1000000000, 9999999999))
        if not Employer.objects.filter(employer_id=employer_id).exists():
            return employer_id


class Employer(models.Model):
    # User relation
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    # Identifiers
    employer_id = models.CharField(
        max_length=12, default=generate_employer_id, unique=True, editable=False)
    # Employer details
    employer_name = models.CharField(max_length=255)
    employer_address = models.CharField(max_length=255, blank=True)
    employer_city = models.CharField(max_length=255, blank=True)
    employer_state = models.CharField(max_length=255, blank=True)
    employer_zip_code = models.CharField(max_length=10, blank=True)
    employer_email_address = models.EmailField(unique=True, db_index=True)
    employer_phone_number = PhoneNumberField(unique=True, blank=True)
    employer_ein_number = models.CharField(
        max_length=20, blank=True, null=True)  # Optional EIN number

    # employee_profile = models.ForeignKey(
    #    'core.EmployeeProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='employer')

    def save(self, *args, **kwargs):
        # Check if this is a new employer
        is_new = self._state.adding  # Better way to check if the instance is new
        super().save(*args, **kwargs)  # Call the "real" save() method.
        # super(Employer, self).save(*args, **kwargs)

        if is_new:
            # This is a new employer, so this user is the first user
            # Add the 'can_view_employer_dashboard' permission to the user
            # Get all permissions
            # Correct way: Iterating over the QuerySet and adding each permission
            employer_permissions = Permission.objects.filter(
                content_type__app_label='employer')
            for permission in employer_permissions:
                self.user.user_permissions.add(permission)

            # Get the 'can_view_employer_dashboard' permission
            # content_type = ContentType.objects.get_for_model(Employer)
            # permission = Permission.objects.get(
            #    codename='can_view_employer_dashboard',
            #    content_type=content_type,
            # )

        # Create EmployeeProfile if it doesn't exist.
        # EmployeeProfile.objects.get_or_create(employer=self)

    def create_invitation(self, email):
        """Create an invitation with a 7-day expiration date."""
        try:
            expiration_date = timezone.now() + timedelta(days=7)
            invitation = Invitation.objects.create(
                employer=self,
                email=email,
                expiration_date=expiration_date
            )
            return invitation
        except Exception as e:
            logger.error(f"Failed to create invitation: {e}")
            raise ValidationError(f"Failed to create invitation: {e}")

    class Meta:
        permissions = [
            ("manage_employer_profile", "Can manage employer profile"),
            ("view_employer_dashboard", "Can view employer dashboard"),
            ("manage_employees", "Can add, edit, or remove employees"),
            ("send_invitations", "Can send invitations to employees"),
            ("view_employee_time_entries", "Can view employee time entries"),
            ("edit_time_entries", "Can approve or edit time entries"),
            ("generate_reports", "Can generate reports"),
            ("manage_billing", "Can manage billing and subscriptions"),
            ("set_alerts_reminders", "Can set up alerts and reminders"),
            ("access_advanced_features", "Can access advanced features"),
            # Add more as needed
        ]

    def __str__(self):
        return self.employer_name


class Invitation(models.Model):
    """Model representing an invitation sent to an email to join as an employer."""
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    # Ensure this field's format is validated through forms or serializers
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    is_accepted = models.BooleanField(default=False)
    expiration_date = models.DateTimeField()
    # Additional fields as required


class EmployerProfile(models.Model):
    """Model representing additional details specific to employer profiles."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    employer = models.ForeignKey(
        Employer, on_delete=models.CASCADE, null=True, blank=True)
    activated = models.BooleanField(default=False)
    website = models.URLField(max_length=200, null=True, blank=True)
    # Add additional fields as required

    def __str__(self):
        return f"{self.user.email} Profile"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created and instance.is_employer:
        EmployerProfile = apps.get_model('employer', 'EmployerProfile')
        EmployerProfile.objects.get_or_create(user=instance)
    # You can also handle EmployeeProfile creation here if needed
