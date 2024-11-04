from django.db.models import Sum
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django.http import JsonResponse
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Case, VerificationCode, Withdrawal, KYCVerification
from .forms import CaseForm, KYCVerificationForm, WithdrawalForm
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from .email_utils import (
    send_recovery_approval_email,
    send_kyc_verification_email,
    send_withdrawal_confirmation_email,
    send_withdrawal_status_email
)
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView
from .models import Withdrawal

from django.shortcuts import render
from core.models import SiteSettings, Testimonial 
from django.core.mail import send_mail
from django.contrib import messages
from core.models import SiteSettings
from .forms import ContactForm



def home(request):
    site_settings = SiteSettings.objects.first()
    testimonials = Testimonial.objects.all()
    context = {
        'site_settings': site_settings,
        'testimonials': testimonials,
    }
    return render(request, 'cases/home.html', context)  # Note: I've kept your original template name

class CaseCreateView(LoginRequiredMixin, CreateView):
    model = Case
    form_class = CaseForm
    template_name = 'cases/create_case.html'

    def get_success_url(self):
        return reverse('cases:dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Your case has been submitted and a welcome email has been sent.")
        return response

class DashboardView(LoginRequiredMixin, ListView):
    model = Case
    template_name = 'cases/dashboard.html'
    context_object_name = 'cases'
    site_settings = SiteSettings.objects.first()

    def get_queryset(self):
        return Case.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        completed_cases = self.get_queryset().filter(status='completed')
        context['completed_amount'] = completed_cases.aggregate(Sum('amount_lost'))['amount_lost__sum'] or 0
        context['total_withdrawn'] = Withdrawal.objects.filter(user=self.request.user, status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        context['recent_withdrawals'] = Withdrawal.objects.filter(user=self.request.user).order_by('-created_at')[:5]
        context['site_settings'] = self.site_settings
        return context

class VerificationView(LoginRequiredMixin, DetailView):
    model = Case
    template_name = 'cases/verification.html'
    context_object_name = 'case'

    def get_queryset(self):
        return Case.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        case = self.get_object()
        
        verification_steps = []
        completed_steps = case.verificationcode_set.filter(is_used=True).values_list('step', flat=True)
        
        for step_num, step_name in VerificationCode.STEP_CHOICES:
            verification_steps.append({
                'number': step_num,
                'name': step_name,
                'completed': step_num in completed_steps,
                'current': step_num == len(completed_steps) + 1
            })
        
        context['verification_steps'] = verification_steps
        context['current_step'] = len(completed_steps) + 1
        return context

    def post(self, request, *args, **kwargs):
        case = self.get_object()
        code = request.POST.get('code')
        current_step = case.verificationcode_set.filter(is_used=True).count() + 1

        try:
            verification = VerificationCode.objects.get(
                case=case,
                step=current_step,
                code=code,
                is_used=False
            )
            
            if verification.is_expired():
                return JsonResponse({
                    'success': False,
                    'error': 'Verification code has expired'
                })

            verification.is_used = True
            verification.save()

            if current_step == 3:
                case.status = 'completed'
                case.save()
                send_recovery_approval_email(case.user)

            return JsonResponse({
                'success': True,
                'message': f'Step {current_step} verified successfully'
            })
            
        except VerificationCode.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Invalid verification code'
            })

class WithdrawalCreateView(LoginRequiredMixin, CreateView):
    model = Withdrawal
    form_class = WithdrawalForm
    template_name = 'cases/create_withdrawal.html'
    success_url = reverse_lazy('cases:dashboard')

    def dispatch(self, request, *args, **kwargs):
        try:
            kyc = KYCVerification.objects.get(user=request.user)
            if not kyc.is_verified:
                messages.warning(request, "You need to complete KYC verification before making a withdrawal.")
                return redirect(reverse('cases:kyc_verification'))
        except KYCVerification.DoesNotExist:
            messages.warning(request, "You need to complete KYC verification before making a withdrawal.")
            return redirect(reverse('cases:kyc_verification'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            response = super().form_valid(form)
            send_withdrawal_confirmation_email(self.request.user, form.instance.amount)
            messages.success(self.request, f"Withdrawal request for ${form.instance.amount} has been submitted. A confirmation email has been sent.")
            return response
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_balance = Case.objects.filter(user=self.request.user, status='completed').aggregate(Sum('amount_lost'))['amount_lost__sum'] or 0
        total_withdrawn = Withdrawal.objects.filter(user=self.request.user, status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        available_balance = total_balance - total_withdrawn
        
        context.update({
            'total_balance': total_balance,
            'total_withdrawn': total_withdrawn,
            'available_balance': available_balance,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class KYCVerificationView(LoginRequiredMixin, CreateView):
    model = KYCVerification
    form_class = KYCVerificationForm
    template_name = 'cases/kyc_verification.html'
    success_url = reverse_lazy('cases:dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'POST':
            kwargs['instance'] = KYCVerification.objects.get_or_create(user=self.request.user)[0]
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        send_kyc_verification_email(self.request.user, "Submitted for Review")
        messages.success(self.request, "Your KYC verification has been submitted for review. A confirmation email has been sent.")
        return response
    
@method_decorator(staff_member_required, name='dispatch')
class AdminWithdrawalUpdateView(UpdateView):
    model = Withdrawal
    fields = ['status']
    template_name = 'admin/withdrawal_update.html'
    success_url = reverse_lazy('admin:cases_withdrawal_changelist')

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.instance.status == 'completed':
            send_withdrawal_status_email(form.instance.user, form.instance.amount, 'completed')
        return response

def privacy_policy(request):
    site_settings = SiteSettings.objects.first()
    context = {
        'site_settings': site_settings,
        'title': 'Privacy Policy',
        'content': site_settings.privacy_policy
    }
    return render(request, 'cases/policy_page.html', context)

def disclaimer(request):
    site_settings = SiteSettings.objects.first()
    context = {
        'site_settings': site_settings,
        'title': 'Disclaimer',
        'content': site_settings.disclaimer
    }
    return render(request, 'cases/policy_page.html', context)

def terms_and_conditions(request):
    site_settings = SiteSettings.objects.first()
    context = {
        'site_settings': site_settings,
        'title': 'Terms and Conditions',
        'content': site_settings.terms_and_conditions
    }
    return render(request, 'cases/policy_page.html', context)

def payment_policy(request):
    site_settings = SiteSettings.objects.first()
    context = {
        'site_settings': site_settings,
        'title': 'Payment Policy',
        'content': site_settings.payment_policy
    }
    return render(request, 'cases/policy_page.html', context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            # Send email
            send_mail(
                f'New contact form submission from {name}',
                message,
                email,
                ['samuelsmar08@gmail.com'],  # Replace with your email
                fail_silently=False,
            )
            
            messages.success(request, 'Your message has been sent. We will contact you soon!')
            return redirect('cases:home')
    else:
        form = ContactForm()
    
    site_settings = SiteSettings.objects.first()
    context = {
        'site_settings': site_settings,
        'form': form,
        'title': 'Contact Us'
    }