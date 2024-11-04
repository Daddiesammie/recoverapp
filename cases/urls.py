# cases/urls.py
from django.urls import path
from . import views, api
from . import views

app_name = 'cases'

urlpatterns = [
    path('', views.home, name='home'),  # Add this new URL pattern
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),  # Update this line
    path('case/new/', views.CaseCreateView.as_view(), name='create_case'),
    path('case/<int:pk>/verify/', views.VerificationView.as_view(), name='verify'),
    path('api/case/<int:case_id>/verify/', api.verify_code, name='api_verify'),
    path('api/case/<int:case_id>/request-code/', api.request_new_code, name='api_request_code'),
    path('withdrawal/new/', views.WithdrawalCreateView.as_view(), name='create_withdrawal'),
    path('kyc-verification/', views.KYCVerificationView.as_view(), name='kyc_verification'),
    path('admin/withdrawal/<int:pk>/update/', views.AdminWithdrawalUpdateView.as_view(), name='admin_withdrawal_update'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('payment-policy/', views.payment_policy, name='payment_policy'),
    path('contact/', views.contact, name='contact'),
]