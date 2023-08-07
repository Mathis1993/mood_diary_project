import time
from datetime import datetime

import pytest
from clients.tests.factories import ClientFactory
from diaries.models import ActivityCategory, MoodDiaryEntry
from diaries.tests.factories import MoodDiaryEntryFactory
from django.utils import timezone
from notifications.models import Notification
from rules.models import RuleTriggeredLog
from rules.rules import (
    ActivityWithPeakMoodRule,
    BaseRule,
    HighMediaUsagePerDayRule,
    PhysicalActivityPerWeekRule,
    RelaxingActivityRule,
)
from rules.tests.factories import RuleFactory


def test_base_rule():
    timestamp = timezone.now()
    rule = BaseRule(client_id=1, requested_at=timestamp)
    assert rule.client_id == 1
    assert rule.requested_at == timestamp
    with pytest.raises(NotImplementedError):
        rule.rule_title
    with pytest.raises(NotImplementedError):
        rule.triggering_allowed()
    with pytest.raises(NotImplementedError):
        rule.get_mood_diary_entries()
    with pytest.raises(NotImplementedError):
        rule.evaluate_preconditions()


@pytest.mark.django_db
def test_concrete_rule():
    class MyRule(BaseRule):
        rule_title = "My Rule"

        def triggering_allowed(self):
            return True

        def get_mood_diary_entries(self):
            return MoodDiaryEntry.objects.none()

        def evaluate_preconditions(self):
            return True

    rule_db = RuleFactory.create(title="My Rule")
    client = ClientFactory.create()
    timestamp = timezone.now()
    rule = MyRule(client_id=client.id, requested_at=timestamp)
    assert rule.client_id == client.id
    assert rule.requested_at == timestamp
    assert rule.rule_title == "My Rule"
    assert rule.rule == rule_db
    assert rule.triggering_allowed() is True
    assert rule.get_mood_diary_entries().exists() is False
    assert rule.evaluate_preconditions() is True
    assert rule.client_subscribed() is False
    assert not Notification.objects.exists()
    assert not RuleTriggeredLog.objects.exists()
    rule.evaluate()  # no effect
    assert not Notification.objects.exists()
    assert not RuleTriggeredLog.objects.exists()
    rule_db.subscribed_clients.add(client)
    assert rule.client_subscribed() is True
    rule.evaluate()  # creates notification and log
    assert Notification.objects.count() == 1
    assert RuleTriggeredLog.objects.count() == 1

    class MyOtherRule(MyRule):
        def triggering_allowed(self):
            return False

    rule = MyOtherRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is False
    rule.evaluate()  # no effect
    assert Notification.objects.count() == 1
    assert RuleTriggeredLog.objects.count() == 1


@pytest.mark.django_db
def test_activity_with_peak_mood_rule():
    client = ClientFactory.create()
    rule_db = RuleFactory.create(title="Activity with peak mood")
    rule_db.subscribed_clients.add(client)
    MoodDiaryEntryFactory.create(mood_diary__client=client, mood__value=0)
    time.sleep(0.1)
    target_entry = MoodDiaryEntryFactory.create(mood_diary__client=client, mood__value=1)
    timestamp = timezone.now()
    time.sleep(0.1)
    MoodDiaryEntryFactory.create(mood_diary__client=client, mood__value=2)
    rule = ActivityWithPeakMoodRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is True
    entries = rule.get_mood_diary_entries()
    assert entries.first().id == target_entry.id
    assert rule.evaluate_preconditions() is False

    time.sleep(0.1)
    new_target_entry = MoodDiaryEntryFactory.create(mood_diary__client=client, mood__value=3)
    new_timestamp = timezone.now()
    rule = ActivityWithPeakMoodRule(client_id=client.id, requested_at=new_timestamp)
    assert rule.get_mood_diary_entries().first() == new_target_entry
    assert not Notification.objects.exists()
    assert not RuleTriggeredLog.objects.exists()
    rule.evaluate()
    assert Notification.objects.count() == 1
    assert RuleTriggeredLog.objects.count() == 1

    rule_db.subscribed_clients.remove(client)
    assert rule.client_subscribed() is False
    rule.evaluate()  # no effect
    assert Notification.objects.count() == 1
    assert RuleTriggeredLog.objects.count() == 1


@pytest.mark.django_db
def test_relaxing_activity_mood_rule():
    client = ClientFactory.create()
    rule_db = RuleFactory.create(title="Relaxing activity")
    rule_db.subscribed_clients.add(client)
    MoodDiaryEntryFactory.create(mood_diary__client=client, activity__category__value="Work")
    time.sleep(0.1)
    target_entry = MoodDiaryEntryFactory.create(
        mood_diary__client=client, activity__category__value="Social"
    )
    timestamp = timezone.now()
    time.sleep(0.1)
    MoodDiaryEntryFactory.create(mood_diary__client=client, activity__category__value="Studies")
    rule = RelaxingActivityRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is True
    entries = rule.get_mood_diary_entries()
    assert entries.first().id == target_entry.id
    assert rule.evaluate_preconditions() is False

    time.sleep(0.1)
    new_target_entry = MoodDiaryEntryFactory.create(
        mood_diary__client=client, activity__category__value=ActivityCategory.relaxing_value
    )
    new_timestamp = timezone.now()
    rule = RelaxingActivityRule(client_id=client.id, requested_at=new_timestamp)
    assert rule.get_mood_diary_entries().first() == new_target_entry
    assert not Notification.objects.exists()
    assert not RuleTriggeredLog.objects.exists()
    rule.evaluate()
    assert Notification.objects.count() == 1
    assert RuleTriggeredLog.objects.count() == 1

    rule_db.subscribed_clients.remove(client)
    assert rule.client_subscribed() is False
    rule.evaluate()  # no effect
    assert Notification.objects.count() == 1
    assert RuleTriggeredLog.objects.count() == 1


@pytest.mark.django_db
def test_physical_activity_per_week_rule(freezer):
    # It is Friday
    freezer.move_to("2023-09-30")
    client = ClientFactory.create()
    rule_db = RuleFactory.create(title="Physical activity per week")
    rule_db.subscribed_clients.add(client)
    # Sunday (does not count)
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        activity__category__value=ActivityCategory.physical_activity_value,
        date="2023-09-24",
        start_time=datetime(2023, 9, 24, 10, 0),
        end_time=datetime(2023, 9, 24, 13, 0),
    )
    # Monday (does count)
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        activity__category__value=ActivityCategory.physical_activity_value,
        date="2023-09-25",
        start_time=datetime(2023, 9, 25, 10, 0),
        end_time=datetime(2023, 9, 25, 11, 0),
    )
    timestamp = timezone.now()
    rule = PhysicalActivityPerWeekRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is True
    assert rule.evaluate_preconditions() is False

    # Tuesday (does count)
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        activity__category__value=ActivityCategory.physical_activity_value,
        date="2023-09-26",
        start_time=datetime(2023, 9, 26, 10, 0),
        end_time=datetime(2023, 9, 26, 12, 0),
    )

    assert rule.evaluate_preconditions() is True
    assert not Notification.objects.exists()
    assert not RuleTriggeredLog.objects.exists()
    rule.evaluate()
    assert Notification.objects.count() == 1
    assert RuleTriggeredLog.objects.count() == 1

    assert rule.triggering_allowed() is False

    freezer.move_to("2023-10-02")

    assert rule.triggering_allowed() is True


@pytest.mark.django_db
def test_high_media_usage_per_day_rule(freezer):
    freezer.move_to("2023-09-30")
    client = ClientFactory.create()
    rule_db = RuleFactory.create(title="High media usage per day")
    rule_db.subscribed_clients.add(client)

    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        activity__category__value=ActivityCategory.media_usage_value,
        date="2023-09-30",
        start_time=datetime(2023, 9, 30, 10, 0),
        end_time=datetime(2023, 9, 30, 13, 0),
    )
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        activity__category__value=ActivityCategory.media_usage_value,
        date="2023-09-30",
        start_time=datetime(2023, 9, 30, 14, 0),
        end_time=datetime(2023, 9, 30, 16, 0),
    )

    timestamp = timezone.now()
    rule = HighMediaUsagePerDayRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is True
    assert rule.evaluate_preconditions() is False

    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        activity__category__value=ActivityCategory.media_usage_value,
        date="2023-09-30",
        start_time=datetime(2023, 9, 30, 17, 0),
        end_time=datetime(2023, 9, 30, 18, 0),
    )

    assert rule.triggering_allowed() is True
    assert rule.evaluate_preconditions() is True
    assert not Notification.objects.exists()
    assert not RuleTriggeredLog.objects.exists()
    rule.evaluate()
    assert Notification.objects.count() == 1
    assert RuleTriggeredLog.objects.count() == 1

    assert rule.triggering_allowed() is False
