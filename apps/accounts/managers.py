from django.contrib.auth.models import BaseUserManager


class SLUserManager(BaseUserManager):
    def create_user(self, sl_avatar_name, **extra_fields):
        if not sl_avatar_name:
            raise ValueError('SL Avatar Name is required')
        user = self.model(sl_avatar_name=sl_avatar_name, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, sl_avatar_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        user = self.model(sl_avatar_name=sl_avatar_name, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user