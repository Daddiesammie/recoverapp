from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Withdrawal
from .email_utils import send_withdrawal_status_email

@receiver(post_save, sender=Withdrawal)
def withdrawal_post_save(sender, instance, created, **kwargs):
    if not created and instance.status == 'completed':
        send_withdrawal_status_email(instance.user, instance.amount, instance.status)