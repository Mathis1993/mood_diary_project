from datetime import date

import factory.fuzzy
from diaries.models import (
    Activity,
    ActivityCategory,
    Emotion,
    Mood,
    MoodDiary,
    MoodDiaryEntry,
    Strain,
    StrainArea,
)
from django.utils import timezone

MOOD_SCALE = {
    -3: "Extremely Unhappy",
    -2: "Unhappy",
    -1: "Somewhat Unhappy",
    0: "Neutral",
    1: "Somewhat Happy",
    2: "Happy",
    3: "Extremely Happy",
}

STRAIN_SCALE = {
    1: "Very Low Strain",
    2: "Low Strain",
    3: "Moderate-Low Strain",
    4: "Neutral",
    5: "Moderate-High Strain",
    6: "High Strain",
    7: "Very High Strain",
}

ACTIVITIES = {
    "Eating": ["Eating", "Drinking"],
    "Sleep": ["Sleeping", "Napping"],
    "Work": ["Working", "School", "Volunteering"],
    "Studies": ["Studying", "Reading", "Homework"],
    "Physical Activity": ["Exercise", "Sports", "Yoga"],
    "Social": ["Socializing", "Partying", "Hanging out with friends"],
    "Relaxation": ["Relaxing", "Meditating", "Praying"],
    "Travel": ["Traveling", "Commuting"],
    "Media Usage": ["Watching TV", "Playing Video Games", "Browsing the Internet"],
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
    emotion = factory.SubFactory("diaries.tests.factories.EmotionFactory")
    mood_and_emotion_info = factory.faker.Faker("sentence", nb_words=10)
    activity = factory.SubFactory("diaries.tests.factories.ActivityFactory")
    strain = factory.SubFactory("diaries.tests.factories.StrainFactory")
    strain_area = factory.SubFactory("diaries.tests.factories.StrainAreaFactory")
    strain_info = factory.faker.Faker("sentence", nb_words=10)


class MoodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Mood
        django_get_or_create = ("value",)

    value = factory.fuzzy.FuzzyChoice([-3, -2, -1, 0, 1, 2, 3])
    label = factory.LazyAttribute(lambda obj: MOOD_SCALE[obj.value])


class EmotionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Emotion
        django_get_or_create = ("value",)

    value = factory.fuzzy.FuzzyChoice(
        [
            "Joy",
            "Sadness",
            "Anger",
            "Fear",
            "Surprise",
            "Disgust",
            "Trust",
            "Anticipation",
        ]
    )


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Activity
        django_get_or_create = ("value",)

    category = factory.SubFactory("diaries.tests.factories.ActivityCategoryFactory")
    value = factory.LazyAttribute(
        lambda obj: factory.fuzzy.FuzzyChoice(ACTIVITIES[obj.category.value]).fuzz()
    )


class ActivityCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActivityCategory
        django_get_or_create = ("value",)

    value = factory.fuzzy.FuzzyChoice(ACTIVITIES.keys())


class StrainFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Strain
        django_get_or_create = ("value",)

    value = factory.fuzzy.FuzzyChoice(list(STRAIN_SCALE.keys()))
    label = factory.LazyAttribute(lambda obj: STRAIN_SCALE[obj.value])


class StrainAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StrainArea
        django_get_or_create = ("value",)

    value = factory.fuzzy.FuzzyChoice(["Friends", "Family", "Job"])
