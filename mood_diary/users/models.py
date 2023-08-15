from __future__ import annotations

from core.models import TrackCreationAndUpdates
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_superuser(self, email: str, password: str):
        if password is None:
            raise TypeError("Superusers must have a password.")

        user = self.model(email=email)
        user.set_password(password)
        user.role = User.Role.ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.first_login_completed = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin, TrackCreationAndUpdates):
    class Meta:
        db_table = "users_users"

    class Role(models.TextChoices):
        ADMIN = "admin"
        COUNSELOR = "counselor"
        CLIENT = "client"

    email = models.EmailField(db_index=True, unique=True, max_length=255)
    role = models.CharField(choices=Role.choices, max_length=255)
    first_login_completed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # The `is_staff` flag is expected by Django to determine who can and cannot
    # log into the Django admin site
    is_staff = models.BooleanField(default=False)

    # The `USERNAME_FIELD` property tells us which field we will use to log in
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    # The BaseUserManager contains a "get_by_natural_key" method using the
    # `USERNAME_FIELD` property during authentication
    objects = UserManager()

    def is_client(self):
        """Used as authorization check."""
        return self.role == User.Role.CLIENT

    def is_counselor(self):
        """Used as authorization check."""
        return self.role == User.Role.COUNSELOR
