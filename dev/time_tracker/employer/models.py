# /employer/models.py


import random
import uuid
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from django import forms
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
# from core.models import EmployeeProfile
from django.apps import apps

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
        max_length=10, unique=True, editable=False, db_index=True)
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

    employee_profile = models.OneToOneField(
        'core.EmployeeProfile', on_delete=models.CASCADE, related_name='employer_profile')

    def save(self, *args, **kwargs):
        EmployeeProfile = apps.get_model('core', 'EmployeeProfile')
        # Check if this is a new employer
        is_new = self.pk is None

        super().save(*args, **kwargs)  # Call the "real" save() method.
        # super(Employer, self).save(*args, **kwargs)

        if is_new:
            # This is a new employer, so this user is the first user
            # Add the 'can_view_employer_dashboard' permission to the user
            # Get all permissions
            permissions = Permission.objects.all()

            # Get the 'can_view_employer_dashboard' permission
            # content_type = ContentType.objects.get_for_model(Employer)
            # permission = Permission.objects.get(
            #    codename='can_view_employer_dashboard',
            #    content_type=content_type,
            # )

            # Add the permission to the user
            self.user.user_permissions.add(permissions)

        # Create EmployeeProfile if it doesn't exist.
        EmployeeProfile.objects.get_or_create(employer=self)

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
            ("can_view_employer_dashboard", "Can view employer dashboard"),
            ("can_send_invitations", "Can send invitations"),
        ]


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
    website = models.URLField(max_length=200, null=True, blank=True)
    # Add additional fields as required
