from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_welcome_email(user):
    subject = 'Welcome to Our Platform'
    context = {
        'user': user,
    }
    message = render_to_string('emails/welcome.html', context)
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=message,
    )

def send_goodbye_email(user):
    # Implement your email sending logic here
    pass