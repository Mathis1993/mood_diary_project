from __future__ import annotations

from datetime import date

from clients.models import Client
from core.models import NormalizedScaleModel, NormalizedStringValueModel, TrackCreationAndUpdates
from django.db import models
from django.db.models import Avg, QuerySet


class MoodDiary(models.Model):
    """
    This is the MoodDiary model representing a mood diary of a client.
    A mood diary has got a one-to-one relationship with a client and
    can have multiple mood diary entries.
    It serves as a container for some methods that target all mood diary
    entries of a client.
    """

    class Meta:
        db_table = "diaries_mood_diaries"

    client = models.OneToOneField(to=Client, on_delete=models.CASCADE, related_name="mood_diary")

    def average_mood_scores_previous_days(self, n_days: int) -> QuerySet:
        """
        Calculate the average mood scores of the previous n days.

        Parameters
        ----------
        n_days: int

        Returns
        -------
        QuerySet
            MoodDiary entities grouped by date and with an aggregated average mood score.
        """
        return (
            self.entries.order_by("-date")
            .values("date")
            .annotate(average_mood=Avg("mood__value"))[:n_days]
        )

    def most_recent_mood_highlights(self, n_highlights: int) -> QuerySet:
        """
        Return the n most recent mood highlights.

        Parameters
        ----------
        n_highlights: int

        Returns
        -------
        QuerySet
            MoodDiary entities ordered by mood score and date.
        """
        return self.entries.order_by("-mood__value", "-date")[:n_highlights]

    def release_entries(self):
        """
        Release all unreleased mood diary entries.

        Returns
        -------
        None
        """
        self.entries.filter(released=False).update(released=True)


class MoodDiaryEntry(TrackCreationAndUpdates):
    """
    This is the MoodDiaryEntry model representing a mood diary entry of a client.
    """

    class Meta:
        db_table = "diaries_mood_diary_entries"
        ordering = ["-date", "-start_time"]

    mood_diary = models.ForeignKey(to=MoodDiary, on_delete=models.CASCADE, related_name="entries")
    released = models.BooleanField(default=False)
    date = models.DateField(default=date.today)
    start_time = models.TimeField()
    end_time = models.TimeField()
    mood = models.ForeignKey(
        to="diaries.Mood", on_delete=models.RESTRICT, related_name="mood_diary_entries"
    )
    activity = models.ForeignKey(
        to="diaries.Activity", on_delete=models.RESTRICT, related_name="mood_diary_entries"
    )
    details = models.TextField(null=True, blank=True, default=None)


class Mood(NormalizedScaleModel):
    """
    This is the Mood model representing the mood scale.
    """

    class Meta:
        db_table = "diaries_moods"
        ordering = ["value"]

    def __str__(self) -> str:
        return f"{self.label} ({self.value})"

    def to_percentage(self) -> int:
        """
        Convert the mood value to a percentage value.

        Returns
        -------
        int
            Rounded percentage value.
        """
        return int(self.value / 7 * 100)

    @staticmethod
    def max_value() -> int:
        """
        Return the maximum value of the mood scale.

        Returns
        -------
        int
        """
        return 3


class Activity(NormalizedStringValueModel):
    """
    This is the Activity model representing an activity.
    """

    class Meta:
        db_table = "diaries_activities"
        ordering = ["category__value_de", "value_de"]

    category = models.ForeignKey(
        to="diaries.ActivityCategory", on_delete=models.CASCADE, related_name="activities"
    )

    def __str__(self) -> str:
        return self.value

    sports_value = "Sports"


class ActivityCategory(NormalizedStringValueModel):
    """
    This is the ActivityCategory model representing an activity category.
    """

    class Meta:
        db_table = "diaries_activity_categories"
        ordering = ["value"]

    def __str__(self) -> str:
        return self.value

    physical_activity_value = "Physical Activity"
    relaxing_value = "Relaxation"
    media_usage_value = "Media"
    food_intake_value = "Food"
