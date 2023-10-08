from core.utils import hash_email
from django.contrib.auth.backends import ModelBackend
from users.models import User


class EmailHashBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            email = kwargs.get(User.EMAIL_FIELD)
            if email is None:
                return
            email_hash = hash_email(email)
        else:
            email_hash = hash_email(username)
        if email_hash is None or password is None:
            return
        try:
            user = User._default_manager.get_by_natural_key(email_hash)
        except User.DoesNotExist:
            return
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
