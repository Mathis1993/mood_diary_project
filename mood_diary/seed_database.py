from clients.tests.factories import ClientFactory
from diaries.tests.factories import (
    ACTIVITIES,
    ActivityFactory,
    MoodDiaryEntryFactory,
    MoodDiaryFactory,
)
from django.conf import settings
from django.contrib.auth import get_user_model
from rules.models import Rule
from rules.rules import EVENT_BASED_RULES, TIME_BASED_RULES
from rules.tests.factories import RuleFactory
from users.tests.factories import UserFactory

User = get_user_model()


def seed_database():
    User.objects.create_superuser(
        email="mathis@mood-diary.de", password=settings.TEST_USER_PASSWORD
    )

    [
        RuleFactory.create(title=rule.rule_title, evaluation=Rule.Evaluation.EVENT_BASED)
        for rule in EVENT_BASED_RULES
    ]
    [
        RuleFactory.create(title=rule.rule_title, evaluation=Rule.Evaluation.TIME_BASED)
        for rule in TIME_BASED_RULES
    ]
    [
        ActivityFactory.create(category__value=category, value=activity)
        for category, activities in ACTIVITIES.items()
        for activity in activities
    ]

    counselor = UserFactory.create(role=User.Role.COUNSELOR)
    client_user = UserFactory.create(role=User.Role.CLIENT)
    client = ClientFactory.create(
        user=client_user, counselor=counselor, subscribed_rules=Rule.objects.all()
    )

    mood_diary = MoodDiaryFactory.create(client=client)
    for _ in range(25):
        MoodDiaryEntryFactory.create(mood_diary=mood_diary)
