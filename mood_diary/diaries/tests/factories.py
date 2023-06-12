from datetime import date

import factory.fuzzy
from diaries.models import Activity, Emotion, Mood, MoodDiary, MoodDiaryEntry, Strain, StrainArea
from django.utils import timezone

MOOD_SCALE = {
    1: "Extremely Unhappy",
    2: "Unhappy",
    3: "Somewhat Unhappy",
    4: "Neutral",
    5: "Somewhat Happy",
    6: "Happy",
    7: "Extremely Happy",
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
        django_get_or_create = ("value",)

    value = factory.fuzzy.FuzzyChoice(list(MOOD_SCALE.keys()))
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
        django_get_or_create = ("value",)

    value = factory.fuzzy.FuzzyChoice(list(STRAIN_SCALE.keys()))
    label = factory.LazyAttribute(lambda obj: STRAIN_SCALE[obj.value])


class StrainAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StrainArea
        django_get_or_create = ("value",)

    value = factory.fuzzy.FuzzyChoice(["Friends", "Family", "Job"])
