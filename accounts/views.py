from django.views.generic import CreateView, UpdateView
from django.contrib import messages  # Correct import for messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, UserProfileForm
from django.views.decorators.http import require_http_methods
from .email_utils import send_goodbye_email, send_welcome_email


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        send_welcome_email(self.request.user)
        return redirect('cases:dashboard')
    
@require_http_methods(["GET", "POST"])
def custom_logout(request):
    if request.user.is_authenticated:
        send_goodbye_email(request.user)
    logout(request)
    return redirect('cases:home')
 
    
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    template_name = 'profile.html'
    success_url = reverse_lazy('cases:dashboard')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Profile updated successfully!')
        return response