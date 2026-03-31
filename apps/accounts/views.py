from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, OTPRequest
from .serializers import (
    SendOTPSerializer, VerifyOTPSerializer,
    UserProfileSerializer, PendingOTPSerializer,
)
from .throttles import OTPRateThrottle
from .utils import fetch_sl_profile_image


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([OTPRateThrottle])
def send_otp(request):
    """Generate OTP for SL avatar. LSL relay picks it up and IMs the user."""
    serializer = SendOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    sl_name = serializer.validated_data['sl_avatar_name']

    # Per-user rate limit
    recent = OTPRequest.objects.filter(
        sl_avatar_name__iexact=sl_name,
        created_at__gte=timezone.now() - timedelta(seconds=settings.OTP_RATE_LIMIT_SECONDS),
    ).first()
    if recent:
        wait = settings.OTP_RATE_LIMIT_SECONDS - (timezone.now() - recent.created_at).seconds
        return Response(
            {'error': f'Please wait {max(wait, 1)} seconds before requesting a new OTP.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # Invalidate previous OTPs
    OTPRequest.objects.filter(sl_avatar_name__iexact=sl_name, is_used=False).update(is_used=True)

    OTPRequest.objects.create(
        sl_avatar_name=sl_name,
        otp_code=OTPRequest.generate_otp(),
        expires_at=timezone.now() + timedelta(seconds=settings.OTP_EXPIRY_SECONDS),
    )

    return Response({
        'message': f'OTP sent to {sl_name} in Second Life. Check your IMs.',
        'expires_in': settings.OTP_EXPIRY_SECONDS,
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_otp(request):
    """Verify OTP and return JWT tokens. Creates account on first login."""
    serializer = VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    sl_name = serializer.validated_data['sl_avatar_name']
    otp_code = serializer.validated_data['otp_code']

    otp = OTPRequest.objects.filter(
        sl_avatar_name__iexact=sl_name, otp_code=otp_code, is_used=False,
    ).order_by('-created_at').first()

    if not otp:
        return Response({'error': 'Invalid OTP code.'}, status=status.HTTP_400_BAD_REQUEST)
    if otp.is_expired:
        return Response({'error': 'OTP has expired.'}, status=status.HTTP_400_BAD_REQUEST)

    otp.is_used = True
    otp.save()

    user = User.objects.filter(sl_avatar_name__iexact=sl_name).first()
    created = False
    if not user:
        user = User.objects.create_user(
            sl_avatar_name=sl_name, is_verified=True,
        )
        created = True
    if not user.is_verified:
        user.is_verified = True
    user.last_seen = timezone.now()
    user.save(update_fields=['is_verified', 'last_seen'])

    refresh = RefreshToken.for_user(user)
    return Response({
        'message': 'Authentication successful.',
        'user': UserProfileSerializer(user).data,
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        },
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    user = request.user
    if user.sl_uuid and not user.profile_image_url:
        img = fetch_sl_profile_image(user.sl_uuid)
        if img:
            user.profile_image_url = img
            user.save(update_fields=['profile_image_url'])
    return Response(UserProfileSerializer(user).data)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    sl_uuid = request.data.get('sl_uuid', '').strip()
    if sl_uuid:
        request.user.sl_uuid = sl_uuid
        img = fetch_sl_profile_image(sl_uuid)
        if img:
            request.user.profile_image_url = img
        request.user.save(update_fields=['sl_uuid', 'profile_image_url'])
    return Response(UserProfileSerializer(request.user).data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def pending_otps(request):
    """LSL relay polls this to pick up OTPs to deliver via llInstantMessage."""
    api_key = request.META.get('HTTP_X_API_KEY', '')
    if api_key != settings.LSL_API_KEY:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    otps = OTPRequest.objects.filter(
        is_used=False, is_delivered=False, expires_at__gt=timezone.now(),
    ).order_by('created_at')[:10]

    data = PendingOTPSerializer(otps, many=True).data
    OTPRequest.objects.filter(id__in=[o.id for o in otps]).update(is_delivered=True)
    return Response({'pending_otps': data})