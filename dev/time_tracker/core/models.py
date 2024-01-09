# core/models.py --> app specific models

import random

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
# Assuming Employer model is correctly defined in employer.models
# from employer.models import Employer
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps  # Import the apps module from django.apps
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError


# UserManager definition


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# Custom user model


class PunchinUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=70, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    # REQUIRED_FIELDS = ['username']

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_employer = models.BooleanField(
        default=False, verbose_name='Employer Status')

    objects = UserManager()

    def save(self, *args, **kwargs):
        # Call the "real" save() method.
        super().save(*args, **kwargs)
        # Only proceed if the database table for EmployeeProfile exists
        try:
            # Only proceed if the database table for EmployeeProfile exists
            if 'core_employeeprofile' in connection.introspection.table_names():
                EmployeeProfile = apps.get_model('core', 'EmployeeProfile')
                EmployeeProfile.objects.get_or_create(user=self)
        except (OperationalError, ProgrammingError):
            # Handle the error or ignore if it's due to missing tables during initial migration
            pass

        # Create EmployeeProfile if it doesn't exist. #
        # EmployeeProfile = apps.get_model('core', 'EmployeeProfile')
        # EmployeeProfile.objects.get_or_create(user=self)

    def __str__(self):
        return self.email


@receiver(post_save, sender=PunchinUser)
def create_employee_profile(sender, instance, created, **kwargs):
    if created:
        try:
            EmployeeProfile = apps.get_model('core', 'EmployeeProfile')
            EmployeeProfile.objects.get_or_create(user=instance)
        except (OperationalError, ProgrammingError):
            # If tables aren't ready, this will skip creating EmployeeProfile
            pass


# Time Entry model for tracking work time


class TimeEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    project = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.clock_in}"


class EmployeeProfile(models.Model):
    # EmployeeProfile model
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Use apps.get_model() to import Employer dynamically
    employer = models.OneToOneField(
        'employer.Employer', on_delete=models.CASCADE)
    # Additional fields can be added here as needed

    # def save(self, *args, **kwargs):
    #    Employer = apps.get_model('employer', 'Employer')

    def __str__(self):
        return f"{self.user.email} profile"

# Add any additional models or logic here as needed

# Assuming 'EmployerProfile' is the model name for the employer's profile


@receiver(post_save, sender=PunchinUser)
def create_employee_profile(sender, instance, created, **kwargs):
    if created:
        try:
            # Attempt to get or create the EmployeeProfile
            EmployeeProfile = apps.get_model('core', 'EmployeeProfile')
            EmployeeProfile.objects.get_or_create(user=instance)
        except (OperationalError, ProgrammingError):
            # If tables aren't ready, this will skip creating EmployeeProfile
            pass


'''
@receiver(post_save, sender=PunchinUser)
def create_employer_profile(sender, instance, created, **kwargs):
    if created and instance.is_employer:  # Assuming 'is_employer' is a field on the user model
        # Lazy import of the EmployerProfile model
        EmployerProfile = apps.get_model('employer', 'EmployerProfile')
        EmployerProfile.objects.create(user=instance)
'''

# post_save.connect(create_employer_profile, sender=PunchinUser)
