from datetime import timedelta
from functools import cached_property

from diaries.models import ActivityCategory, Mood, MoodDiary, MoodDiaryEntry
from django.db import models
from django.utils import timezone
from notifications.models import Notification
from rules.models import Rule, RuleTriggeredLog
from rules.utils import get_beginning_of_current_week


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
        return self.rule.subscribed_clients.filter(id=self.client_id).exists()

    def persist_rule_triggering(self):
        RuleTriggeredLog.objects.create(rule=self.rule, client_id=self.client_id)

    def create_notification(self):
        message = self.rule.conclusion_message
        Notification.objects.create(client_id=self.client_id, message=message)

    def evaluate(self):
        if not self.client_subscribed():
            return
        if not self.triggering_allowed():
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
            created_at__gte=get_beginning_of_current_week(),
        ).exists()

    def get_mood_diary_entries(self) -> models.QuerySet[MoodDiaryEntry]:
        return MoodDiary.objects.get(client_id=self.client_id).entries.filter(
            date__gte=get_beginning_of_current_week(),
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
            created_at__gte=timezone.now().date(),
        ).exists()

    def get_mood_diary_entries(self) -> models.QuerySet[MoodDiaryEntry]:
        return MoodDiary.objects.get(client_id=self.client_id).entries.filter(
            date=timezone.now().date(),
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
