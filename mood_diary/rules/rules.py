from datetime import timedelta
from functools import cached_property

from diaries.models import Activity, ActivityCategory, Mood, MoodDiary, MoodDiaryEntry
from django.db import models
from django.utils import timezone
from notifications.models import Notification
from rules.models import Rule, RuleTriggeredLog
from rules.utils import get_beginning_of_week, get_end_of_week


class BaseRule:
    """
    Base class for all rules. Each rule class must declare a rule_title property linking to
    a rule title in the database and implement the triggering_allowed, get_mood_diary_entries
    and evaluate_preconditions methods.
    When creating a rule instance, the client_id and a timestamp pertaining to the exact time
    the evaluation of the rule was requested at must be provided.
    To evaluate a rule, call the evaluate method. This method checks if the client is
    subscribed to the rule, if the rule is allowed to trigger right now and if the
    preconditions for the rule are met.
    If all of these conditions are met, the rule triggering is logged in the database and
    a notification for the respective client is created.
    """

    def __init__(self, client_id: int, requested_at: timezone.datetime):
        self.client_id = client_id
        self.requested_at = requested_at

    @property
    def rule_title(self) -> str:
        raise NotImplementedError

    @cached_property
    def rule(self) -> Rule:
        return Rule.objects.get(title=self.rule_title)

    def triggering_allowed(self) -> bool:
        """
        Checks if the rule is allowed to trigger right now.
        If, for example, the rule is only allowed to trigger once a day, this method should
        return False if the rule has already been triggered today.
        """
        raise NotImplementedError

    def get_mood_diary_entries(self) -> models.QuerySet[MoodDiaryEntry]:
        raise NotImplementedError

    def evaluate_preconditions(self) -> bool:
        """
        Checks if the preconditions for the rule are met.
        For example, if the rule is based on a threshold, this method should check if the
        threshold has been reached.
        """
        raise NotImplementedError

    def client_subscribed(self) -> bool:
        """
        Checks if the client is subscribed to the rule at the moment.
        """
        return self.rule.rule_users.filter(client_id=self.client_id, active=True).exists()

    def mood_diary_exists(self) -> bool:
        """
        Checks if the client has a mood diary and logged any entries.
        """
        return (
            MoodDiary.objects.filter(client_id=self.client_id).exists()
            and MoodDiary.objects.get(client_id=self.client_id).entries.exists()
        )

    def persist_rule_triggering(self):
        RuleTriggeredLog.objects.create(
            rule=self.rule, client_id=self.client_id, created_at=self.requested_at
        )

    def create_notification(self):
        message = self.rule.conclusion_message
        Notification.objects.create(client_id=self.client_id, message=message, rule_id=self.rule.id)

    def evaluate(self):
        if not self.client_subscribed():
            return
        if not self.triggering_allowed():
            return
        if not self.mood_diary_exists():
            return
        if not self.evaluate_preconditions():
            return
        self.persist_rule_triggering()
        self.create_notification()


class ActivityWithPeakMoodRule(BaseRule):
    """
    Rule checking if the last activity the client did before the rule evaluation was
    requested had the highest mood value available.
    """

    rule_title = "Activity with peak mood"

    def triggering_allowed(self) -> bool:
        return True

    def get_mood_diary_entries(self) -> models.QuerySet[MoodDiaryEntry]:
        """
        Get the mood diary entry that was last edited before rule evaluation was requested.
        """
        return (
            MoodDiary.objects.get(client_id=self.client_id)
            .entries.filter(updated_at__lte=self.requested_at)
            .order_by("-updated_at")
        )

    def evaluate_preconditions(self) -> bool:
        mood_diary_entries = self.get_mood_diary_entries()
        return mood_diary_entries and mood_diary_entries.first().mood.value == Mood.max_value()


class RelaxingActivityRule(ActivityWithPeakMoodRule):
    """
    Rule checking if the last activity the client did before the rule evaluation was
    requested was a relaxing activity.
    """

    rule_title = "Relaxing activity"

    def evaluate_preconditions(self) -> bool:
        mood_diary_entries = self.get_mood_diary_entries()
        return (
            mood_diary_entries.exists()
            and mood_diary_entries.first().activity.category.value
            == ActivityCategory.relaxing_value
        )


class PhysicalActivityPerWeekRule(BaseRule):
    """
    Rule checking if the client has done at least 150 minutes of physical activity this week.
    """

    rule_title = "Physical activity per week"

    def triggering_allowed(self) -> bool:
        return not RuleTriggeredLog.objects.filter(
            rule=self.rule,
            client_id=self.client_id,
            created_at__gte=get_beginning_of_week(self.requested_at),
        ).exists()

    def get_mood_diary_entries(self) -> models.QuerySet[MoodDiaryEntry]:
        return MoodDiary.objects.get(client_id=self.client_id).entries.filter(
            date__gte=get_beginning_of_week(self.requested_at),
        )

    def evaluate_preconditions(self) -> bool:
        relevant_entries = self.get_mood_diary_entries().filter(
            activity__category__value=ActivityCategory.physical_activity_value
        )
        if not relevant_entries.exists():
            return False
        duration_sum = relevant_entries.annotate(
            duration=models.F("end_time") - models.F("start_time")
        ).aggregate(models.Sum("duration"))["duration__sum"]
        return duration_sum >= timedelta(minutes=150)


class HighMediaUsagePerDayRule(BaseRule):
    """
    Rule checking if the client has spent more than 6 hours on media usage today.
    """

    rule_title = "High media usage per day"

    def triggering_allowed(self) -> bool:
        return not RuleTriggeredLog.objects.filter(
            rule=self.rule,
            client_id=self.client_id,
            created_at__gte=self.requested_at.date(),
        ).exists()

    def get_mood_diary_entries(self) -> models.QuerySet[MoodDiaryEntry]:
        return MoodDiary.objects.get(client_id=self.client_id).entries.filter(
            date=self.requested_at.date(),
        )

    def evaluate_preconditions(self) -> bool:
        relevant_entries = self.get_mood_diary_entries().filter(
            activity__category__value=ActivityCategory.media_usage_value
        )
        if not relevant_entries.exists():
            return False
        duration_sum = relevant_entries.annotate(
            duration=models.F("end_time") - models.F("start_time")
        ).aggregate(models.Sum("duration"))["duration__sum"]
        return duration_sum >= timedelta(hours=6)


class LowMediaUsagePerDayRule(HighMediaUsagePerDayRule):
    """
    Rule checking if the client has spent less than 30 minutes on media usage today.
    """

    rule_title = "Low media usage per day"

    def evaluate_preconditions(self) -> bool:
        relevant_entries = self.get_mood_diary_entries().filter(
            activity__category__value=ActivityCategory.media_usage_value
        )
        if not relevant_entries.exists():
            return True
        duration_sum = relevant_entries.annotate(
            duration=models.F("end_time") - models.F("start_time")
        ).aggregate(models.Sum("duration"))["duration__sum"]
        return duration_sum <= timedelta(minutes=30)


class FourteenDaysMoodAverageRule(BaseRule):
    """
    Rule checking if the client has got a mean mood value of less than 0 for at least 9
    out of the last 14 days.
    """

    rule_title = "Fourteen days mood average"

    def triggering_allowed(self) -> bool:
        # There are entries for the last 14 days
        entries_for_last_fourteen_days = (
            MoodDiary.objects.get(client_id=self.client_id)
            .entries.filter(
                date__gt=self.requested_at.date() - timedelta(days=14),
            )
            .values_list("date", flat=True)
            .distinct()
            .count()
            == 14
        )
        # Rule was not triggered in the last 14 days
        rule_not_triggered_in_previous_fourteen_days = not RuleTriggeredLog.objects.filter(
            rule=self.rule,
            client_id=self.client_id,
            created_at__gt=self.requested_at.date() - timedelta(days=14),
        ).exists()
        return entries_for_last_fourteen_days and rule_not_triggered_in_previous_fourteen_days

    def get_mood_diary_entries(self) -> models.QuerySet[MoodDiaryEntry]:
        return MoodDiary.objects.get(client_id=self.client_id).entries.filter(
            date__gt=self.requested_at.date() - timedelta(days=14),
        )

    def evaluate_preconditions(self) -> bool:
        relevant_entries = self.get_mood_diary_entries()
        if not relevant_entries.exists():
            return False
        days_with_mood_avg_below_zero = (
            relevant_entries.values("date")
            .annotate(mood_avg=models.Avg("mood__value"))
            .filter(mood_avg__lt=0)
            .count()
        )
        return days_with_mood_avg_below_zero >= 9


# ToDo(ME-07.08.23): Less than 1 here but less than 0 for rule above?
class FourteenDaysMoodMaximumRule(FourteenDaysMoodAverageRule):
    """
    Rule checking if the client has got a max mood value of less than 1 for the last 14 days.
    """

    rule_title = "Fourteen days mood maximum"

    def evaluate_preconditions(self) -> bool:
        relevant_entries = self.get_mood_diary_entries()
        if not relevant_entries.exists():
            return False
        max_mood_value = relevant_entries.aggregate(models.Max("mood__value"))["mood__value__max"]
        return max_mood_value < 1


class UnsteadyFoodIntakeRule(BaseRule):
    """
    Rule checking if the client has eaten less than 3 meals per day.
    """

    rule_title = "Unsteady food intake"

    def triggering_allowed(self) -> bool:
        return not RuleTriggeredLog.objects.filter(
            rule=self.rule,
            client_id=self.client_id,
            created_at__gte=self.requested_at.date(),
        ).exists()

    def get_mood_diary_entries(self) -> models.QuerySet[MoodDiaryEntry]:
        return MoodDiary.objects.get(client_id=self.client_id).entries.filter(
            date=self.requested_at.date(),
        )

    def evaluate_preconditions(self) -> bool:
        relevant_entries = self.get_mood_diary_entries().filter(
            activity__value=Activity.food_intake_value
        )
        return relevant_entries.count() < 3


class PositiveMoodChangeBetweenActivitiesRule(BaseRule):
    """
    Rule checking if the client has a positive mood change between two consecutive activities.
    """

    rule_title = "Positive mood change between activities"

    def triggering_allowed(self) -> bool:
        return True

    def get_mood_diary_entries(self) -> models.QuerySet[MoodDiaryEntry]:
        entry_last_edit = (
            MoodDiary.objects.get(client_id=self.client_id)
            .entries.filter(updated_at__lte=self.requested_at)
            .order_by("-updated_at")
            .first()
        )
        if entry_last_edit is None:
            return MoodDiary.objects.none()
        entry_before_last_edited_one = (
            MoodDiary.objects.get(client_id=self.client_id)
            .entries.filter(date__lte=entry_last_edit.date, end_time__lte=entry_last_edit.end_time)
            .exclude(id=entry_last_edit.id)
            .order_by("-end_time")
            .first()
        )
        if entry_before_last_edited_one is None:
            return MoodDiary.objects.none()
        if entry_last_edit.activity == entry_before_last_edited_one.activity:
            return MoodDiary.objects.none()
        return (
            MoodDiary.objects.get(client_id=self.client_id)
            .entries.filter(id__in=[entry_last_edit.id, entry_before_last_edited_one.id])
            .order_by("-end_time")
        )

    def evaluate_preconditions(self) -> bool:
        relevant_entries = self.get_mood_diary_entries()
        if not relevant_entries.exists():
            return False
        mood_values = relevant_entries.values_list("mood__value", flat=True)
        return mood_values[0] - mood_values[1] >= 2


class NegativeMoodChangeBetweenActivitiesRule(PositiveMoodChangeBetweenActivitiesRule):
    """
    Rule checking if the client has a negative mood change between two consecutive activities.
    """

    rule_title = "Negative mood change between activities"

    def evaluate_preconditions(self) -> bool:
        relevant_entries = self.get_mood_diary_entries()
        if not relevant_entries.exists():
            return False
        mood_values = relevant_entries.values_list("mood__value", flat=True)
        return mood_values[0] - mood_values[1] <= -2


class DailyAverageMoodImprovingRule(BaseRule):
    """
    Rule checking if the client has a higher average mood than the day before.
    """

    rule_title = "Daily average mood improving"

    def triggering_allowed(self) -> bool:
        return not RuleTriggeredLog.objects.filter(
            rule=self.rule,
            client_id=self.client_id,
            created_at__gte=self.requested_at.date(),
        ).exists()

    def get_mood_diary_entries(self) -> models.QuerySet[MoodDiaryEntry]:
        return MoodDiary.objects.get(client_id=self.client_id).entries.filter(
            date__gte=self.requested_at.date() - timedelta(days=1),
            date__lte=self.requested_at.date(),
        )

    def evaluate_preconditions(self) -> bool:
        relevant_entries = self.get_mood_diary_entries()
        if not relevant_entries.exists():
            return False
        if relevant_entries.values_list("date", flat=True).distinct().count() != 2:
            return False
        mood_values_per_day = (
            relevant_entries.values("date")
            .annotate(avg_mood=models.Avg("mood__value"))
            .order_by("-date")
        )
        return mood_values_per_day[0]["avg_mood"] > mood_values_per_day[1]["avg_mood"]


class PhysicalActivityPerWeekIncreasingRule(BaseRule):
    """
    Rule checking if the client has a higher physical activity than the week before.
    """

    rule_title = "Physical activity per week increasing"

    def triggering_allowed(self) -> bool:
        # Only to be triggered on Sundays
        if self.requested_at.weekday() != 6:
            return False
        return not RuleTriggeredLog.objects.filter(
            rule=self.rule,
            client_id=self.client_id,
            created_at__gte=get_beginning_of_week(self.requested_at),
        ).exists()

    def get_mood_diary_entries(self) -> models.QuerySet[MoodDiaryEntry]:
        return MoodDiary.objects.get(client_id=self.client_id).entries.filter(
            date__gte=get_beginning_of_week(self.requested_at - timedelta(days=7)),
            date__lte=self.requested_at.date(),
        )

    def evaluate_preconditions(self) -> bool:
        relevant_entries = self.get_mood_diary_entries().filter(
            activity__category__value=ActivityCategory.physical_activity_value
        )
        if not relevant_entries.exists():
            return False
        duration_sum_last_week = (
            relevant_entries.filter(
                date__gte=get_beginning_of_week(self.requested_at) - timedelta(days=7),
                date__lte=get_end_of_week(self.requested_at) - timedelta(days=7),
            )
            .annotate(duration=models.F("end_time") - models.F("start_time"))
            .aggregate(models.Sum("duration"))["duration__sum"]
        )
        duration_sum_current_week = (
            relevant_entries.filter(
                date__gte=get_beginning_of_week(self.requested_at),
                date__lte=self.requested_at.date(),
            )
            .annotate(duration=models.F("end_time") - models.F("start_time"))
            .aggregate(models.Sum("duration"))["duration__sum"]
        )
        if duration_sum_last_week is None or duration_sum_current_week is None:
            return False
        return duration_sum_current_week > duration_sum_last_week


TIME_BASED_RULES = [
    LowMediaUsagePerDayRule,
    FourteenDaysMoodAverageRule,
    FourteenDaysMoodMaximumRule,
    UnsteadyFoodIntakeRule,
    DailyAverageMoodImprovingRule,
    PhysicalActivityPerWeekIncreasingRule,
]

EVENT_BASED_RULES = [
    ActivityWithPeakMoodRule,
    RelaxingActivityRule,
    PhysicalActivityPerWeekRule,
    HighMediaUsagePerDayRule,
    PositiveMoodChangeBetweenActivitiesRule,
    NegativeMoodChangeBetweenActivitiesRule,
]
