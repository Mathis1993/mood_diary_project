from clients.models import Client
from core.models import NormalizedScaleModel, NormalizedStringValueModel, TrackCreationAndUpdates
from django.db import models
from django.utils import timezone


class MoodDiary(models.Model):
    class Meta:
        db_table = "diaries_mood_diaries"

    client = models.OneToOneField(to=Client, on_delete=models.CASCADE, related_name="mood_diary")


class MoodDiaryEntry(TrackCreationAndUpdates):
    class Meta:
        db_table = "diaries_mood_diary_entries"

    mood_diary = models.ForeignKey(to=MoodDiary, on_delete=models.CASCADE, related_name="entries")
    released = models.BooleanField(default=False)
    start_time = models.TimeField(null=True, blank=True, default=None)
    end_time = models.TimeField(default=timezone.now, null=True, blank=True)
    mood = models.ForeignKey(
        to="diaries.Mood", on_delete=models.RESTRICT, related_name="mood_diary_entries"
    )
    emotion = models.ForeignKey(
        to="diaries.Emotion",
        on_delete=models.RESTRICT,
        related_name="mood_diary_entries",
        null=True,
        blank=True,
        default=None,
    )
    mood_and_emotion_info = models.TextField(null=True, blank=True, default=None)
    activity = models.ForeignKey(
        to="diaries.Activity", on_delete=models.RESTRICT, related_name="mood_diary_entries"
    )
    strain = models.ForeignKey(
        to="diaries.Strain",
        on_delete=models.RESTRICT,
        related_name="mood_diary_entries",
        null=True,
        blank=True,
        default=None,
    )
    strain_area = models.ForeignKey(
        to="diaries.StrainArea",
        on_delete=models.RESTRICT,
        related_name="mood_diary_entries",
        null=True,
        blank=True,
        default=None,
    )
    strain_info = models.TextField(null=True, blank=True, default=None)


class Mood(NormalizedScaleModel):
    class Meta:
        db_table = "diaries_moods"

    def __str__(self):
        return f"{self.label} ({self.value})"


class Emotion(NormalizedStringValueModel):
    class Meta:
        db_table = "diaries_emotions"

    def __str__(self):
        return self.value


class Activity(NormalizedStringValueModel):
    class Meta:
        db_table = "diaries_activities"

    def __str__(self):
        return self.value


class Strain(NormalizedScaleModel):
    class Meta:
        db_table = "diaries_strains"

    def __str__(self):
        return f"{self.label} ({self.value})"


class StrainArea(NormalizedStringValueModel):
    class Meta:
        db_table = "diaries_strain_areas"

    def __str__(self):
        return self.value
