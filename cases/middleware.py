# cases/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from .models import Case

class VerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.path.startswith('/case/'):
            try:
                case_id = int(request.path.split('/')[2])
                case = Case.objects.get(id=case_id, user=request.user)
                if case.status == 'approved':
                    verification_codes = case.verificationcode_set.filter(is_used=True)
                    request.current_step = len(verification_codes) + 1
            except (IndexError, ValueError, Case.DoesNotExist):
                pass

        response = self.get_response(request)
        return response