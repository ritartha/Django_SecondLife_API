import uuid
import random
import string
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import SLUserManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sl_avatar_name = models.CharField(max_length=100, unique=True, db_index=True)
    sl_uuid = models.CharField(max_length=36, blank=True, default='')
    profile_image_url = models.URLField(blank=True, default='')
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(null=True, blank=True)

    objects = SLUserManager()
    USERNAME_FIELD = 'sl_avatar_name'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'sl_users'

    def __str__(self):
        return self.sl_avatar_name


class OTPRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sl_avatar_name = models.CharField(max_length=100, db_index=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)

    class Meta:
        db_table = 'otp_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f'OTP for {self.sl_avatar_name}'

    @staticmethod
    def generate_otp():
        return ''.join(random.choices(string.digits, k=6))

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired