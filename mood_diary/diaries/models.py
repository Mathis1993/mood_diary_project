from __future__ import annotations

from datetime import date

from clients.models import Client
from core.models import NormalizedScaleModel, NormalizedStringValueModel, TrackCreationAndUpdates
from django.db import models
from django.db.models import Avg, QuerySet


class MoodDiary(models.Model):
    class Meta:
        db_table = "diaries_mood_diaries"

    client = models.OneToOneField(to=Client, on_delete=models.CASCADE, related_name="mood_diary")

    def average_mood_scores_previous_days(self, n_days: int) -> QuerySet:
        return (
            self.entries.order_by("-date")
            .values("date")
            .annotate(average_mood=Avg("mood__value"))[:n_days]
        )

    def most_recent_mood_highlights(self, n_highlights: int) -> QuerySet:
        return self.entries.order_by("-mood__value", "-date")[:n_highlights]

    def release_entries(self):
        self.entries.filter(released=False).update(released=True)


class MoodDiaryEntry(TrackCreationAndUpdates):
    class Meta:
        db_table = "diaries_mood_diary_entries"

    mood_diary = models.ForeignKey(to=MoodDiary, on_delete=models.CASCADE, related_name="entries")
    released = models.BooleanField(default=False)
    date = models.DateField(default=date.today)
    start_time = models.TimeField()
    end_time = models.TimeField()
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
        ordering = ["value"]

    def __str__(self):
        return f"{self.label} ({self.value})"

    def to_percentage(self) -> int:
        return int(self.value / 7 * 100)

    @staticmethod
    def max_value() -> int:
        return 7


class Emotion(NormalizedStringValueModel):
    class Meta:
        db_table = "diaries_emotions"

    def __str__(self):
        return self.value


class Activity(NormalizedStringValueModel):
    class Meta:
        db_table = "diaries_activities"
        ordering = ["value"]

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
