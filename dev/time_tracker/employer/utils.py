# employer/utils.py

from django.core.mail import send_mail
from django.conf import settings


def send_email_invitation(invitation):
    # Define the email properties
    subject = 'You have been invited to join our platform'
    message = f'Hi, you have been invited to join our platform. Please use this invitation: {
        invitation}'
    from_email = 'support@stritstax.com'  # Replace with your email
    to_email = [invitation.email]  # Replace with the employee's email

    # Send the email
    send_mail(subject, message, from_email, to_email)


def send_email(subject, message, recipient_list, html_message=None):
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from,
              recipient_list, html_message=html_message)
