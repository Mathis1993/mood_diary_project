import factory.fuzzy
from notifications.models import Notification


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    client = factory.SubFactory("clients.tests.factories.ClientFactory")
    message = factory.Faker("text", max_nb_chars=200)
    viewed = factory.fuzzy.FuzzyChoice([True, False])
    rule = factory.SubFactory("rules.tests.factories.RuleFactory")
