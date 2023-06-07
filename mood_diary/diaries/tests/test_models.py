import pytest
from diaries.models import MoodDiaryEntry
from diaries.tests.factories import (
    ActivityFactory,
    EmotionFactory,
    MoodDiaryFactory,
    MoodFactory,
    StrainAreaFactory,
    StrainFactory,
)
from django.utils import timezone


@pytest.mark.django_db
def test_mood_diary_entry():
    mood_diary = MoodDiaryFactory.create()
    mood = MoodFactory.create()
    emotion = EmotionFactory.create()
    activity = ActivityFactory.create()
    strain = StrainFactory.create()
    strain_area = StrainAreaFactory.create()

    # All fields of MoodDiaryEntry filled
    mood_diary_entry_1 = MoodDiaryEntry.objects.create(
        mood_diary=mood_diary,
        released=False,
        start_time=timezone.now() - timezone.timedelta(hours=1),
        end_time=timezone.now(),
        mood=mood,
        emotion=emotion,
        mood_and_emotion_info="blorg",
        activity=activity,
        strain=strain,
        strain_area=strain_area,
        strain_info="blepp",
    )

    assert mood_diary_entry_1.mood_diary == mood_diary
    assert mood_diary_entry_1.start_time < mood_diary_entry_1.end_time
    assert mood_diary_entry_1.released is False
    assert mood_diary_entry_1.mood == mood
    assert mood_diary_entry_1.emotion == emotion
    assert mood_diary_entry_1.mood_and_emotion_info == "blorg"
    assert mood_diary_entry_1.activity == activity
    assert mood_diary_entry_1.strain == strain
    assert mood_diary_entry_1.strain_area == strain_area
    assert mood_diary_entry_1.strain_info == "blepp"

    # Some non-required fields are not filled
    mood_diary_entry_2 = MoodDiaryEntry.objects.create(
        mood_diary=mood_diary,
        mood=mood,
        emotion=emotion,
        activity=activity,
        strain=strain,
        strain_info="blepp",
    )

    assert mood_diary_entry_2.start_time is None
    assert mood_diary_entry_2.end_time is not None
    assert mood_diary_entry_2.mood_and_emotion_info is None
    assert mood_diary_entry_2.strain_area is None

    # Only required fields are filled
    mood_diary_entry_3 = MoodDiaryEntry.objects.create(
        mood_diary=mood_diary,
        mood=mood,
        activity=activity,
    )

    assert mood_diary_entry_3.emotion is None
    assert mood_diary_entry_3.strain is None
    assert mood_diary_entry_3.strain_info is None
