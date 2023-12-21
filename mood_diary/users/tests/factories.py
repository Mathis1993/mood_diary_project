import factory.fuzzy
from core.utils import hash_email
from django.conf import settings
from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email_hash",)

    email = factory.Sequence(lambda n: "user{0}@example.com".format(n))
    email_hash = factory.LazyAttribute(lambda obj: hash_email(obj.email))
    password = factory.PostGenerationMethodCall("set_password", settings.TEST_USER_PASSWORD)
    role = factory.fuzzy.FuzzyChoice(["admin", "counselor", "client"])
    first_login_completed = False
    is_staff = False
