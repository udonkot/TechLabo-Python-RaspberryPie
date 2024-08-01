from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def _create_user(self, email, account_id, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, account_id=account_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, account_id, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email=email, account_id=account_id, password=password, **extra_fields)

    def create_superuser(self, email, account_id, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email=email, account_id=account_id, password=password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    account_id = models.CharField(_('account_id'), max_length=10, unique=True)
    email = models.EmailField(_('email'), unique=True)
    first_name = models.CharField(_('first_name'), max_length=30, blank=True)
    last_name = models.CharField(_('last_name'), max_length=150, blank=True)
    username = models.CharField(_('username'), max_length=150, blank=True)

    is_superuser = models.BooleanField(_('is_superuser'), default=False)
    is_staff = models.BooleanField(_('is_staff'), default=False)
    is_active = models.BooleanField(_('is_active'), default=True)

    objects = UserManager()

    USERNAME_FIELD = 'account_id'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.account_id
