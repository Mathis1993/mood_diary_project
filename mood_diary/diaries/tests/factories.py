from datetime import date

import factory.fuzzy
from diaries.models import Activity, Emotion, Mood, MoodDiary, MoodDiaryEntry, Strain, StrainArea
from django.utils import timezone

MOOD_SCALE = {
    "Extremely Unhappy": 1,
    "Unhappy": 2,
    "Somewhat Unhappy": 3,
    "Neutral": 4,
    "Somewhat Happy": 5,
    "Happy": 6,
    "Extremely Happy": 7,
}

STRAIN_SCALE = {
    "Very Low Strain": 1,
    "Low Strain": 2,
    "Moderate-Low Strain": 3,
    "Neutral": 4,
    "Moderate-High Strain": 5,
    "High Strain": 6,
    "Very High Strain": 7,
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
    date = date.today()
    start_time = timezone.now() - timezone.timedelta(hours=1)
    end_time = timezone.now()
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
        django_get_or_create = ("label",)

    label = factory.fuzzy.FuzzyChoice(list(MOOD_SCALE.keys()))
    value = factory.LazyAttribute(lambda obj: MOOD_SCALE[obj.label])


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

    value = factory.fuzzy.FuzzyChoice(
        [
            "Eating meals",
            "Sleeping",
            "Working or studying",
            "Exercising or engaging in physical activities",
            "Socializing with friends or family",
            "Relaxing or pursuing hobbies",
            "Running errands or doing chores",
            "Commuting or traveling",
        ]
    )


class StrainFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Strain
        django_get_or_create = ("label",)

    label = factory.fuzzy.FuzzyChoice(list(STRAIN_SCALE.keys()))
    value = factory.LazyAttribute(lambda obj: STRAIN_SCALE[obj.label])


class StrainAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StrainArea
        django_get_or_create = ("value",)

    value = factory.fuzzy.FuzzyChoice(["Friends", "Family", "Job"])
