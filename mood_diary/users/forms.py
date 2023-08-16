from core.forms import BaseModelForm, FormWithUIClassMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm

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
