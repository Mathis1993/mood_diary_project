import pytest
from diaries.models import MoodDiaryEntry
from diaries.tests.factories import (
    ActivityFactory,
    EmotionFactory,
    MoodDiaryEntryFactory,
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


@pytest.mark.django_db
def test_mood_diary_entry_average_mood_scores_previous_days():
    mood_diary = MoodDiaryFactory.create()
    MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-01", mood__value=1)
    MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-01", mood__value=2)
    MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-01", mood__value=3)
    MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-02", mood__value=4)
    MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-02", mood__value=4)
    MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-03", mood__value=2)
    MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-03", mood__value=3)
    MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-03", mood__value=4)

    # last four days (although only data for three days exists)
    average_mood_scores = mood_diary.average_mood_scores_previous_days(4)

    assert average_mood_scores.count() == 3
    assert average_mood_scores[0]["average_mood"] == 3.0  # 2023-10-03
    assert average_mood_scores[1]["average_mood"] == 4.0  # 2023-10-02
    assert average_mood_scores[2]["average_mood"] == 2.0  # 2023-10-01

    # last two days (without third day)
    average_mood_scores = mood_diary.average_mood_scores_previous_days(2)

    assert average_mood_scores.count() == 2
    assert average_mood_scores[0]["average_mood"] == 3.0  # 2023-10-03
    assert average_mood_scores[1]["average_mood"] == 4.0  # 2023-10-02


@pytest.mark.django_db
def test_mood_diary_entry_most_recent_mood_highlights():
    mood_diary = MoodDiaryFactory.create()
    MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-01", mood__value=1)
    MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-01", mood__value=2)
    target_3 = MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-01", mood__value=5)
    target_1 = MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-01", mood__value=4)
    target_2 = MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-02", mood__value=4)
    MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-02", mood__value=3)
    MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-03", mood__value=2)
    MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-03", mood__value=3)
    target_4 = MoodDiaryEntryFactory.create(mood_diary=mood_diary, date="2023-10-03", mood__value=6)

    most_recent_highlights = mood_diary.most_recent_mood_highlights(4)

    assert most_recent_highlights.count() == 4
    assert most_recent_highlights[0].id == target_4.id
    assert most_recent_highlights[1].id == target_3.id
    assert most_recent_highlights[2].id == target_2.id
    assert most_recent_highlights[3].id == target_1.id


@pytest.mark.django_db
def test_release_entries():
    mood_diary = MoodDiaryFactory.create()
    MoodDiaryEntryFactory.create_batch(3, mood_diary=mood_diary, released=False)
    MoodDiaryEntryFactory.create_batch(2, mood_diary=mood_diary, released=True)

    mood_diary.release_entries()

    unreleased_entries = mood_diary.entries.filter(released=False)
    assert unreleased_entries.count() == 0
    released_entries = mood_diary.entries.filter(released=True)
    assert released_entries.count() == 5
