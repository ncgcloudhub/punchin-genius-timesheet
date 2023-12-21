# employer/utils.py
from django.core.mail import send_mail


def send_email_invitation(invitation):
    # Define the email properties
    subject = 'You have been invited to join our platform'
    message = f'Hi, you have been invited to join our platform. Please use this invitation: {invitation}'
    from_email = 'support@trionxai.com'  # Replace with your email
    to_email = [invitation.email]  # Replace with the employee's email

    # Send the email
    send_mail(subject, message, from_email, to_email)
