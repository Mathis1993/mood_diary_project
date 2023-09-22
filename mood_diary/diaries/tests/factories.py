from datetime import date

import factory.fuzzy
from diaries.content.moods import MOOD_SCALE_DE_EN
from diaries.models import Activity, ActivityCategory, Mood, MoodDiary, MoodDiaryEntry
from django.utils import timezone

ACTIVITIES = {
    "Sleep": ["Sleeping"],
    "Food": ["Meal"],
    "Studies": ["Lecture"],
    "Work": ["Part-time job"],
    "Social": ["Meeting friends"],
    "Physical Activity": ["Sports"],
    "Relaxation": ["Meditation"],
    "Media": ["PC Gaming"],
    "Errands": ["Shopping"],
    "Culture and Creativity": ["Listening to music"],
    "Problematic Behavior": ["Ruminating"],
    "Transportation": ["Driving in a car"],
    "Other": ["Other activity"],
}


class MoodDiaryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MoodDiary
        django_get_or_create = ("client",)

    client = factory.SubFactory("clients.tests.factories.ClientFactory")


class MoodDiaryEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MoodDiaryEntry

    mood_diary = factory.SubFactory(MoodDiaryFactory)
    released = factory.fuzzy.FuzzyChoice([True, False])
    date = factory.LazyAttribute(lambda obj: date.today())
    start_time = factory.LazyAttribute(lambda obj: timezone.now() - timezone.timedelta(hours=1))
    end_time = factory.LazyAttribute(lambda obj: timezone.now())
    mood = factory.SubFactory("diaries.tests.factories.MoodFactory")
    details = factory.faker.Faker("sentence", nb_words=10)
    activity = factory.SubFactory("diaries.tests.factories.ActivityFactory")


class MoodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Mood
        django_get_or_create = ("value",)

    value = factory.fuzzy.FuzzyChoice([-3, -2, -1, 0, 1, 2, 3])
    label = factory.LazyAttribute(lambda obj: list(MOOD_SCALE_DE_EN[obj.value].keys())[0])


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Activity
        django_get_or_create = ("value", "category")

    category = factory.SubFactory("diaries.tests.factories.ActivityCategoryFactory")
    value = factory.LazyAttribute(
        lambda obj: factory.fuzzy.FuzzyChoice(ACTIVITIES[obj.category.value]).fuzz()
    )


class ActivityCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActivityCategory
        django_get_or_create = ("value",)

    value = factory.fuzzy.FuzzyChoice(ACTIVITIES.keys())
