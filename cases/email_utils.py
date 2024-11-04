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

def send_recovery_approval_email(user):
    subject = 'Account Recovery Approved'
    context = {
        'user': user,
    }
    message = render_to_string('emails/recovery_approved.html', context)
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=message,
    )

def send_kyc_verification_email(user, status):
    subject = 'KYC Verification Status Update'
    context = {
        'user': user,
        'status': status,
    }
    message = render_to_string('emails/kyc_verification.html', context)
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=message,
    )

def send_withdrawal_confirmation_email(user, amount):
    subject = 'Withdrawal Confirmation'
    context = {
        'user': user,
        'amount': amount,
    }
    message = render_to_string('emails/withdrawal_confirmation.html', context)
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=message,
    )

def send_withdrawal_status_email(user, amount, status):
    subject = 'Withdrawal Status Update'
    context = {
        'user': user,
        'amount': amount,
        'status': status,
    }
    message = render_to_string('emails/withdrawal_status.html', context)
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=message,)