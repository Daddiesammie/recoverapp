# cases/utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_verification_code_email(case, code, step):
    context = {
        'user': case.user,
        'case': case,
        'code': code,
        'step': step,
    }
    
    subject = f'Verification Code for Step {step}'
    message = render_to_string('emails/verification_code.html', context)
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [case.user.email],
        html_message=message,
    )


