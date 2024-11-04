# cases/models.py
from django.db import models
from django.conf import settings
import random
import string
from django.utils import timezone
from datetime import timedelta

class Case(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewing', 'Under Review'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.CharField(max_length=255)
    amount_lost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100)
    wallet_address = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Case #{self.id} - {self.user.username}"

    def get_verification_progress(self):
        """Returns the number of completed verification steps"""
        return self.verificationcode_set.filter(is_used=True).count()

    def is_verification_complete(self):
        """Checks if all verification steps are completed"""
        return self.get_verification_progress() == 3

    def get_current_step(self):
        """Returns the current verification step (1-3) or None if complete"""
        completed_steps = self.get_verification_progress()
        return None if completed_steps >= 3 else completed_steps + 1

class VerificationCode(models.Model):
    STEP_CHOICES = [
        (1, 'Identity Verification'),
        (2, 'Document Verification'),
        (3, 'Final Verification')
    ]
    
    case = models.ForeignKey('Case', on_delete=models.CASCADE)
    step = models.IntegerField(choices=STEP_CHOICES)
    code = models.CharField(max_length=20)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True)

    class Meta:
        unique_together = ['case', 'step']
        ordering = ['step']

    def save(self, *args, **kwargs):
        # Generate code if not provided
        if not self.code:
            self.code = self.generate_code()
        
        # Set expiration if not provided
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=30)
            
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if the verification code has expired"""
        return self.expires_at and timezone.now() > self.expires_at

    def is_valid(self):
        """Check if the code is still valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()

    @staticmethod
    def generate_code():
        """Generate a random 6-character alphanumeric code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def __str__(self):
        return f"Case #{self.case.id} - {self.get_step_display()} Code"

    @classmethod
    def create_for_case(cls, case, step):
        """Create a new verification code for a specific case and step"""
        existing_code = cls.objects.filter(case=case, step=step, is_used=False).first()
        if existing_code:
            if existing_code.is_expired():
                existing_code.delete()
            else:
                return existing_code

        return cls.objects.create(
            case=case,
            step=step,
            code=cls.generate_code(),
            expires_at=timezone.now() + timedelta(minutes=30)
        )

    def mark_as_used(self):
        """Mark the verification code as used and update case status if needed"""
        if not self.is_used and not self.is_expired():
            self.is_used = True
            self.save()
            
            # If this was the final step, mark the case as completed
            if self.step == 3:
                self.case.status = 'completed'
                self.case.save()
            
            return True
        return False
    
class KYCVerification(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    document_type = models.CharField(max_length=50, choices=[
        ('passport', 'Passport'),
        ('drivers_license', 'Driver\'s License'),
        ('national_id', 'National ID')
    ])
    document_number = models.CharField(max_length=100)
    document_image = models.ImageField(upload_to='kyc_documents/')

    def __str__(self):
        return f"KYC Verification for {self.user.username}"

    def verify(self):
        self.is_verified = True
        self.verification_date = timezone.now()
        self.save()

class Withdrawal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected')
    ], default='pending')

    def __str__(self):
        return f"Withdrawal #{self.id} - {self.user.username} - ${self.amount}"

    def save(self, *args, **kwargs):
        if not self.id:  # Only check KYC verification on creation
            try:
                kyc = KYCVerification.objects.get(user=self.user)
                if not kyc.is_verified:
                    raise ValueError("KYC verification is required for withdrawals.")
            except KYCVerification.DoesNotExist:
                raise ValueError("KYC verification is required for withdrawals.")
        super().save(*args, **kwargs)
        
