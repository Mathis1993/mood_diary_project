from core.forms import BaseModelForm, FormWithUIClassMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm

User = get_user_model()


class UserEmailForm(BaseModelForm):
    """
    A form for updating a user's email address.
    """

    class Meta:
        model = User
        fields = [
            "email",
        ]


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
