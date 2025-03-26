from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime, timedelta
import random

CUSTOMER, DRIVER = ('Customer', 'Driver')

class User(AbstractUser):
    ROLES = (
        (DRIVER, DRIVER),
        (CUSTOMER, CUSTOMER)
    )
    username = models.CharField(max_length=150, unique=False)
    phone = PhoneNumberField(unique=True)
    role = models.CharField(max_length=30, choices=ROLES, default=CUSTOMER)
    user_image = models.ImageField(upload_to='user/images', null=True, blank=True)
    created_at = models.DateTimeField(_("date joined"), auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['created_at']

    def __str__(self):
        return str(self.phone)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'access': str(refresh.access_token),
            'refresh_token': str(refresh),
        }
        