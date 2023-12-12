import factory.fuzzy
from notifications.models import Notification


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    client = factory.SubFactory("clients.tests.factories.ClientFactory")
    message = factory.Faker("text", max_nb_chars=200)
    viewed = factory.fuzzy.FuzzyChoice([True, False])
    rule = factory.SubFactory("rules.tests.factories.RuleFactory")


class PushSubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "notifications.PushSubscription"

    client = factory.SubFactory("clients.tests.factories.ClientFactory")
    subscription = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/c-g36SB-_FU:APA91bFVHgwBE7Qw81RgXU6SXZ2pRlW1SV44s1oUMI9FX8JT-uCTJAJDD1jCvyYVYofbVcQG2f9CNqo1ujenI6BMiomelh5pO-MBFVE8bInFb9c9bbj8AlWMPiTrmb6oGkE6sMqIawIS",  # noqa E501
        "expirationTime": "null",
        "keys": {
            "p256dh": "BKbfcPS4ivMtp-zpVqyIQI60M5RLlol8582AhDl9V6TukmEiWzAbjrrLRPhHmoyHhbsrhRkdAXa7Sfe13aNrurQ",  # noqa E501
            "auth": "Stn8bCwWxn7CLiR_2hLeDA",
        },
    }
