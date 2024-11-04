# cases/api.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Case, VerificationCode

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_code(request, case_id):
    try:
        case = Case.objects.get(id=case_id, user=request.user)
        if case.status != 'approved':
            return Response({'error': 'Case is not approved for verification'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        current_step = case.verificationcode_set.filter(is_used=True).count() + 1
        if current_step > 3:
            return Response({'error': 'Verification process already completed'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        code = request.data.get('code')
        verification = VerificationCode.objects.filter(
            case=case,
            step=current_step,
            code=code,
            is_used=False,
            expires_at__gt=timezone.now()
        ).first()

        if not verification:
            return Response({'error': 'Invalid or expired code'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        verification.is_used = True
        verification.save()

        if current_step == 3:
            case.status = 'completed'
            case.save()

        return Response({'success': True, 'step': current_step})

    except Case.DoesNotExist:
        return Response({'error': 'Case not found'}, 
                      status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_new_code(request, case_id):
    try:
        case = Case.objects.get(id=case_id, user=request.user)
        current_step = case.verificationcode_set.filter(is_used=True).count() + 1
        
        if current_step > 3:
            return Response({'error': 'Verification process already completed'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if a verification code already exists for the current step
        existing_code = VerificationCode.objects.filter(case=case, step=current_step, is_used=False).first()
        if existing_code:
            return Response({'error': 'A verification code for this step already exists'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Generate new verification code
        code = VerificationCode.generate_code()
        expires_at = timezone.now() + timedelta(minutes=30)
        
        VerificationCode.objects.create(
            case=case,
            code=code,
            step=current_step,
            expires_at=expires_at
        )

        # Send code via email
        send_verification_code_email(case, code, current_step)

        return Response({'success': True, 'message': 'New code sent'})

    except Case.DoesNotExist:
        return Response({'error': 'Case not found'}, 
                        status=status.HTTP_404_NOT_FOUND)