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

    def save(self, *args, **kwargs):
        """Override save method to ensure a unique employer_id is generated."""
        if not self.employer_id:
            self.employer_id = generate_employer_id()
        super(Employer, self).save(*args, **kwargs)

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
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employerprofile')
    # Add additional fields as required
