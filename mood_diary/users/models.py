from __future__ import annotations

from core.models import TrackCreationAndUpdates
from core.utils import hash_email
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_superuser(
        self, email: str = None, email_hash: str = None, password: str = None, **kwargs
    ):
        """
        The email should be provided here as a raw string in either the `email` or the
        `email_hash` argument. This is done to keep compatibility with pytest-django's
        test client fixtures like `admin_client`.
        """
        if email is None and email_hash is None:
            raise TypeError("Superusers must have an email address.")
        if password is None:
            raise TypeError("Superusers must have a password.")

        if email is None:
            email = email_hash

        user = self.model(email=email)
        user.set_password(password)
        user.role = User.Role.ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.first_login_completed = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin, TrackCreationAndUpdates):
    """
    This is the custom user model that is used for the project.
    It represents a user of the application.
    The users can have one of three roles: `ADMIN`, `COUNSELOR` or `CLIENT`.
    """

    class Meta:
        db_table = "users_users"

    class Role(models.TextChoices):
        ADMIN = "admin"
        COUNSELOR = "counselor"
        CLIENT = "client"

    # empty placeholder, field is just temporarily filled when django's
    # internal password reset is used
    email = models.EmailField(null=True, blank=True, default=None)
    # just store email hash for better security
    email_hash = models.CharField(db_index=True, unique=True, max_length=64)
    role = models.CharField(choices=Role.choices, max_length=255)
    first_login_completed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # The `is_staff` flag is expected by Django to determine who can and cannot
    # log into the Django admin site
    is_staff = models.BooleanField(default=False)

    # The `USERNAME_FIELD` property tells us which field we will use to log in
    USERNAME_FIELD = "email_hash"
    EMAIL_FIELD = "email"

    # The BaseUserManager contains a "get_by_natural_key" method using the
    # `USERNAME_FIELD` property during authentication
    objects = UserManager()

    def is_admin(self) -> bool:
        """
        Used as an authorization check.
        """
        return self.role == User.Role.ADMIN

    def is_client(self) -> bool:
        """
        Used as an authorization check.
        """
        return self.role == User.Role.CLIENT

    def is_counselor(self) -> bool:
        """
        Used as an authorization check.
        """
        return self.role == User.Role.COUNSELOR

    def save(self, *args, **kwargs):
        if self.email:
            self.email_hash = hash_email(self.email)
            self.email = None
        super().save(*args, **kwargs)
