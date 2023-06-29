import factory.fuzzy
from notifications.models import Notification


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    user = factory.SubFactory("users.tests.factories.UserFactory")
    message = factory.Faker("text", max_nb_chars=200)
    viewed = factory.fuzzy.FuzzyChoice([True, False])
