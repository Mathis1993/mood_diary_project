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
    push_notifications_granted = None
    client_key_encrypted = factory.Sequence(lambda n: "client_key_encrypted_{0}".format(n))

    @factory.post_generation
    def subscribed_rules(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for rule in extracted:
                self.subscribed_rules.add(rule)
