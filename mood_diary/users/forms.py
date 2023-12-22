from typing import Generator

from core.forms import FormWithUIClassMixin
from core.utils import hash_email
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserModel,
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


# Because the email address is used to encrypt the mood diary entry detail field,
# we disable the possibility to change the email address for now.
# class UserEmailForm(BaseModelForm):
#     """
#     A form for updating a user's email address.
#     """
#
#     class Meta:
#         model = User
#         fields = [
#             "email",
#         ]


class CustomPasswordChangeForm(FormWithUIClassMixin, PasswordChangeForm):
    """
    A form for changing a user's password including the "form-control" class
    for all fields.
    """

    pass


class CustomSetPasswordForm(FormWithUIClassMixin, SetPasswordForm):
    """
    A form for setting a user's password including the "form-control" class
    for all fields.
    """

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

    def save(
        self,
        domain_override=None,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name="registration/password_reset_email.html",
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        email_field_name = UserModel.get_email_field_name()
        for user in self.get_users(email):
            user_email = getattr(user, email_field_name)
            # User with empty email field for token generation as the user
            # calling the password reset link later will have an empty
            # email field as only the hashed email is stored in the database.
            user_no_email = user
            user_no_email.email = None
            context = {
                "email": user_email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user_no_email),
                "protocol": "https" if use_https else "http",
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name,
                email_template_name,
                context,
                from_email,
                user_email,
                html_email_template_name=html_email_template_name,
            )
