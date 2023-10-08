from typing import Generator

from core.forms import BaseModelForm, FormWithUIClassMixin
from core.utils import hash_email
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm

User = get_user_model()


class UserEmailForm(BaseModelForm):
    class Meta:
        model = User
        fields = [
            "email",
        ]


class CustomPasswordChangeForm(FormWithUIClassMixin, PasswordChangeForm):
    pass


class CustomSetPasswordForm(FormWithUIClassMixin, SetPasswordForm):
    pass


class CustomPasswordResetForm(FormWithUIClassMixin, PasswordResetForm):
    def get_users(self, email: str) -> Generator:
        """
        Given an email, return matching user(s) who should receive a reset.
        This sets the usually empty email field on the user model so that the email
        can be set although in the database, only the hashed email is stored.
        """
        hashed_email = hash_email(email)
        username_field_name = User.USERNAME_FIELD
        active_users = User._default_manager.filter(
            **{
                "%s__iexact" % username_field_name: hashed_email,
                "is_active": True,
            }
        )
        [u.__setattr__(User.EMAIL_FIELD, email) for u in active_users]
        return (u for u in active_users if u.has_usable_password())
