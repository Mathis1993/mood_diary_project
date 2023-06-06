import factory.fuzzy
from clients.models import Client


class ClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Client
        django_get_or_create = ("user",)

    user = factory.SubFactory("users.tests.factories.UserFactory", role="client")
    identifier = factory.Sequence(lambda n: "identifier_{0}".format(n))
    counselor = factory.SubFactory("users.tests.factories.UserFactory", role="counselor")
    active = factory.fuzzy.FuzzyChoice([True, False])
