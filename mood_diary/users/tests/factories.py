import factory.fuzzy
from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: "user{0}@example.com".format(n))
    password = factory.PostGenerationMethodCall("set_password", "password1")
    role = factory.fuzzy.FuzzyChoice(["admin", "counselor", "client"])
    first_login_completed = False
    is_staff = False
