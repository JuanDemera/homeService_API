from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        GUEST = 'guest', _('Guest')
        CONSUMER = 'consumer', _('Consumer')
        PROVIDER = 'provider', _('Provider')
        MANAGEMENT = 'management', _('Management')

    username = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=15, unique=True, db_index=True)
    password = models.TextField()
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.GUEST)
    
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    disabled = models.BooleanField(default=False)
    disabled_at = models.DateTimeField(null=True, blank=True)
    disabled_reason = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone']

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return self.username

    @property
    def full_role(self):
        return self.get_role_display()