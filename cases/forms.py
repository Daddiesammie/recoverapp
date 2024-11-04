# cases/forms.py
from django import forms
from .models import Case, Withdrawal
from django.db.models import Sum
from .models import KYCVerification

class KYCVerificationForm(forms.ModelForm):
    class Meta:
        model = KYCVerification
        fields = ['document_type', 'document_number', 'document_image']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'bg-gray-800 text-cyber-blue border border-cyber-pink rounded-md p-2 w-full'}),
            'document_number': forms.TextInput(attrs={'class': 'bg-gray-800 text-cyber-blue border border-cyber-pink rounded-md p-2 w-full'}),
            'document_image': forms.FileInput(attrs={'class': 'bg-gray-800 text-cyber-blue border border-cyber-pink rounded-md p-2 w-full', 'accept': 'image/*'}),
        }

class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['company', 'amount_lost', 'payment_method', 'wallet_address', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    



class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
        fields = ['amount']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if self.user:
            total_balance = self.user.case_set.filter(status='completed').aggregate(Sum('amount_lost'))['amount_lost__sum'] or 0
            total_withdrawn = Withdrawal.objects.filter(user=self.user, status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
            available_balance = total_balance - total_withdrawn
            if amount > available_balance:
                raise forms.ValidationError(f"Insufficient funds. Available balance: ${available_balance}")
        return amount

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 4}))