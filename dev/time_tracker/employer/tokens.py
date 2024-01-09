# /employer/tokens.py

from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
# Adjust according to your actual User model
from django.contrib.auth import get_user_model


User = get_user_model()


class EmployerActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


employer_activation_token = EmployerActivationTokenGenerator()
