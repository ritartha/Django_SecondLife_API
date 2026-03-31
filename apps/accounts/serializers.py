from rest_framework import serializers
from .models import User, OTPRequest


class SendOTPSerializer(serializers.Serializer):
    sl_avatar_name = serializers.CharField(max_length=100)

    def validate_sl_avatar_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Avatar name is too short.')
        return value


class VerifyOTPSerializer(serializers.Serializer):
    sl_avatar_name = serializers.CharField(max_length=100)
    otp_code = serializers.CharField(max_length=6, min_length=6)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'sl_avatar_name', 'sl_uuid', 'profile_image_url',
            'is_verified', 'date_joined', 'last_seen',
        ]
        read_only_fields = fields


class PendingOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPRequest
        fields = ['id', 'sl_avatar_name', 'otp_code', 'created_at']
        read_only_fields = fields