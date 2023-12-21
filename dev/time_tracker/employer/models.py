# \employer\models.py
from django.db import models
import uuid
from datetime import timedelta
from django.utils import timezone  # Import the timezone module

# Create your models here.


class Employer(models.Model):
    name = models.CharField(max_length=255)

    contact_email = models.EmailField(unique=True)  # Add this line for email
    contact_phone_number = models.CharField(
        max_length=20)  # Add this line for phone number
    # Add any other fields you want here

    def create_invitation(self, email):
        # Set the expiration date to 7 days from now
        expiration_date = timezone.now() + timedelta(days=7)
        # Create the invitation instance
        invitation = Invitation.objects.create(
            employer=self,
            email=email,
            expiration_date=expiration_date
        )
        return invitation


class Invitation(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    is_accepted = models.BooleanField(default=False)
    expiration_date = models.DateTimeField()
    # Add other necessary fields as required
