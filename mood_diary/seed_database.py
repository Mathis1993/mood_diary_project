from clients.tests.factories import ClientFactory
from diaries.tests.factories import MoodDiaryEntryFactory, MoodDiaryFactory
from django.conf import settings
from django.contrib.auth import get_user_model
from users.tests.factories import UserFactory

User = get_user_model()


def seed_database():
    User.objects.create_superuser(
        email="mathis@mood-diary.de", password=settings.TEST_USER_PASSWORD
    )
    counselor = UserFactory.create(role=User.Role.COUNSELOR)
    client_user = UserFactory.create(role=User.Role.CLIENT)
    client = ClientFactory.create(user=client_user, counselor=counselor)
    mood_diary = MoodDiaryFactory.create(client=client)
    for _ in range(25):
        MoodDiaryEntryFactory.create(mood_diary=mood_diary)
