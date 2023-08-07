import time
from datetime import date, datetime, timedelta

import pytest
from clients.tests.factories import ClientFactory
from diaries.models import Activity, ActivityCategory, MoodDiaryEntry
from diaries.tests.factories import MoodDiaryEntryFactory, MoodDiaryFactory, MoodFactory
from django.utils import timezone
from notifications.models import Notification
from rules.models import RuleTriggeredLog
from rules.rules import (
    ActivityWithPeakMoodRule,
    BaseRule,
    DailyAverageMoodImprovingRule,
    FourteenDaysMoodAverageRule,
    FourteenDaysMoodMaximumRule,
    HighMediaUsagePerDayRule,
    NegativeMoodChangeBetweenActivitiesRule,
    PhysicalActivityPerWeekIncreasingRule,
    PhysicalActivityPerWeekRule,
    PositiveMoodChangeBetweenActivitiesRule,
    RelaxingActivityRule,
    UnsteadyFoodIntakeRule,
)
from rules.tests.factories import RuleFactory


@pytest.mark.django_db
def test_base_rule():
    timestamp = timezone.now()
    rule = BaseRule(client_id=1, requested_at=timestamp)
    assert rule.client_id == 1
    assert rule.requested_at == timestamp
    assert rule.mood_diary_exists() is False
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
    MoodDiaryFactory.create(client=client)
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


@pytest.mark.django_db
def test_fourteen_days_mood_average_rule(freezer):
    freezer.move_to("2023-09-30")
    client = ClientFactory.create()
    rule_db = RuleFactory.create(title="Fourteen days mood average")
    rule_db.subscribed_clients.add(client)

    # 13 days of bad mood
    [
        MoodDiaryEntryFactory.create(
            mood_diary__client=client, mood__value=-1, date=date(2023, 9, 30) - timedelta(days=i)
        )
        for i in range(13)
    ]

    timestamp = timezone.now()
    rule = FourteenDaysMoodAverageRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is False
    assert rule.evaluate_preconditions() is True

    # 14th day of bad mood
    MoodDiaryEntryFactory.create(
        mood_diary__client=client, mood__value=-1, date=date(2023, 9, 30) - timedelta(days=13)
    )
    assert rule.triggering_allowed() is True
    assert rule.evaluate_preconditions() is True

    # Now 6 out of 14 days with a mood average >= 0
    [
        MoodDiaryEntryFactory.create(
            mood_diary__client=client, mood__value=3, date=date(2023, 9, 30) - timedelta(days=i)
        )
        for i in range(6)
    ]
    assert rule.triggering_allowed() is True
    assert rule.evaluate_preconditions() is False

    # Now 5 out of 14 days with a mood average >= 0, so 9 with a mood average < 0
    MoodDiaryEntryFactory.create(mood_diary__client=client, mood__value=-3, date=date(2023, 9, 30))
    assert rule.triggering_allowed() is True
    assert rule.evaluate_preconditions() is True
    assert not Notification.objects.exists()
    assert not RuleTriggeredLog.objects.exists()
    rule.evaluate()
    assert Notification.objects.count() == 1
    assert RuleTriggeredLog.objects.count() == 1

    assert rule.triggering_allowed() is False

    freezer.move_to("2023-10-07")
    timestamp = timezone.now()
    rule = FourteenDaysMoodAverageRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is False

    freezer.move_to("2023-10-15")
    timestamp = timezone.now()
    rule = FourteenDaysMoodAverageRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is False
    [
        MoodDiaryEntryFactory.create(
            mood_diary__client=client, date=date(2023, 10, 15) - timedelta(days=i)
        )
        for i in range(14)
    ]
    assert rule.triggering_allowed() is True


@pytest.mark.django_db
def test_fourteen_days_mood_maximum_rule(freezer):
    freezer.move_to("2023-09-30")
    client = ClientFactory.create()
    rule_db = RuleFactory.create(title="Fourteen days mood maximum")
    rule_db.subscribed_clients.add(client)

    # 13 days of bad mood
    [
        MoodDiaryEntryFactory.create(
            mood_diary__client=client, mood__value=-1, date=date(2023, 9, 30) - timedelta(days=i)
        )
        for i in range(13)
    ]

    timestamp = timezone.now()
    rule = FourteenDaysMoodMaximumRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is False
    assert rule.evaluate_preconditions() is True

    # 14th day of bad mood
    MoodDiaryEntryFactory.create(
        mood_diary__client=client, mood__value=-1, date=date(2023, 9, 30) - timedelta(days=13)
    )
    assert rule.triggering_allowed() is True
    assert rule.evaluate_preconditions() is True
    assert rule.triggering_allowed() is True
    assert rule.evaluate_preconditions() is True

    # Add a good mood day
    MoodDiaryEntryFactory.create(mood_diary__client=client, mood__value=3, date=date(2023, 9, 27))
    assert rule.triggering_allowed() is True
    assert rule.evaluate_preconditions() is False

    freezer.move_to("2023-10-07")
    timestamp = timezone.now()
    rule = FourteenDaysMoodMaximumRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is False

    freezer.move_to("2023-10-15")
    timestamp = timezone.now()
    rule = FourteenDaysMoodMaximumRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is False
    [
        MoodDiaryEntryFactory.create(
            mood_diary__client=client, mood__value=-2, date=date(2023, 10, 15) - timedelta(days=i)
        )
        for i in range(14)
    ]
    assert rule.triggering_allowed() is True
    assert not Notification.objects.exists()
    assert not RuleTriggeredLog.objects.exists()
    rule.evaluate()
    assert Notification.objects.count() == 1
    assert RuleTriggeredLog.objects.count() == 1

    assert rule.triggering_allowed() is False


@pytest.mark.django_db
def test_unsteady_food_intake_rule(freezer):
    freezer.move_to("2023-09-30")
    client = ClientFactory.create()
    MoodDiaryFactory.create(client=client)
    rule_db = RuleFactory.create(title="Unsteady food intake")
    rule_db.subscribed_clients.add(client)

    timestamp = timezone.now()
    rule = UnsteadyFoodIntakeRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is True
    assert rule.evaluate_preconditions() is True
    # first meal
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 9, 30),
        activity__value=Activity.food_intake_value,
    )
    assert rule.triggering_allowed() is True
    assert rule.evaluate_preconditions() is True
    # second meal
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 9, 30),
        activity__value=Activity.food_intake_value,
    )
    assert rule.triggering_allowed() is True
    assert rule.evaluate_preconditions() is True
    # third meal
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 9, 30),
        activity__value=Activity.food_intake_value,
    )
    assert rule.triggering_allowed() is True
    assert rule.evaluate_preconditions() is False

    freezer.move_to("2023-10-01")
    timestamp = timezone.now()
    rule = UnsteadyFoodIntakeRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is True
    assert rule.evaluate_preconditions() is True
    assert not Notification.objects.exists()
    assert not RuleTriggeredLog.objects.exists()
    rule.evaluate()
    assert Notification.objects.count() == 1
    assert RuleTriggeredLog.objects.count() == 1
    assert rule.triggering_allowed() is False


@pytest.mark.django_db
def test_positive_mood_change_between_activities_rule():
    client = ClientFactory.create()
    MoodDiaryFactory.create(client=client)
    rule_db = RuleFactory.create(title="Positive mood change between activities")
    rule_db.subscribed_clients.add(client)

    # first activity
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 9, 30),
        activity__value="a",
        mood__value=-3,
        start_time=datetime(2023, 9, 30, 10, 0),
        end_time=datetime(2023, 9, 30, 11, 0),
    )
    timestamp = timezone.now()
    rule = PositiveMoodChangeBetweenActivitiesRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is True
    assert rule.get_mood_diary_entries().count() == 0
    assert rule.evaluate_preconditions() is False

    # second activity
    second_activity = MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 9, 30),
        activity__value="b",
        mood__value=-2,
        start_time=datetime(2023, 9, 30, 11, 0),
        end_time=datetime(2023, 9, 30, 12, 0),
    )
    timestamp = timezone.now()
    rule = PositiveMoodChangeBetweenActivitiesRule(client_id=client.id, requested_at=timestamp)
    assert rule.get_mood_diary_entries().count() == 2
    assert rule.evaluate_preconditions() is False

    # third activity (same one as before)
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 9, 30),
        activity__value="b",
        mood__value=0,
        start_time=datetime(2023, 9, 30, 12, 0),
        end_time=datetime(2023, 9, 30, 13, 0),
    )
    timestamp = timezone.now()
    rule = PositiveMoodChangeBetweenActivitiesRule(client_id=client.id, requested_at=timestamp)
    assert rule.get_mood_diary_entries().count() == 0
    assert rule.evaluate_preconditions() is False

    # fourth activity
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 9, 30),
        activity__value="c",
        mood__value=2,
        start_time=datetime(2023, 9, 30, 13, 0),
        end_time=datetime(2023, 9, 30, 14, 0),
    )
    timestamp = timezone.now()
    rule = PositiveMoodChangeBetweenActivitiesRule(client_id=client.id, requested_at=timestamp)
    assert rule.get_mood_diary_entries().count() == 2
    assert rule.evaluate_preconditions() is True

    # Update second activity
    new_mood = MoodFactory.create(value=1)
    second_activity.mood = new_mood
    second_activity.save()
    timestamp = timezone.now()
    rule = PositiveMoodChangeBetweenActivitiesRule(client_id=client.id, requested_at=timestamp)
    assert rule.get_mood_diary_entries().count() == 2
    assert rule.evaluate_preconditions() is True
    assert not Notification.objects.exists()
    assert not RuleTriggeredLog.objects.exists()
    rule.evaluate()
    assert Notification.objects.count() == 1
    assert RuleTriggeredLog.objects.count() == 1


@pytest.mark.django_db
def test_negative_mood_change_between_activities_rule():
    client = ClientFactory.create()
    MoodDiaryFactory.create(client=client)
    rule_db = RuleFactory.create(title="Negative mood change between activities")
    rule_db.subscribed_clients.add(client)

    # first activity
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 9, 30),
        activity__value="a",
        mood__value=3,
        start_time=datetime(2023, 9, 30, 10, 0),
        end_time=datetime(2023, 9, 30, 11, 0),
    )
    timestamp = timezone.now()
    rule = NegativeMoodChangeBetweenActivitiesRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is True
    assert rule.get_mood_diary_entries().count() == 0
    assert rule.evaluate_preconditions() is False

    # second activity
    second_activity = MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 9, 30),
        activity__value="b",
        mood__value=2,
        start_time=datetime(2023, 9, 30, 11, 0),
        end_time=datetime(2023, 9, 30, 12, 0),
    )
    timestamp = timezone.now()
    rule = NegativeMoodChangeBetweenActivitiesRule(client_id=client.id, requested_at=timestamp)
    assert rule.get_mood_diary_entries().count() == 2
    assert rule.evaluate_preconditions() is False

    # third activity (same one as before)
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 9, 30),
        activity__value="b",
        mood__value=0,
        start_time=datetime(2023, 9, 30, 12, 0),
        end_time=datetime(2023, 9, 30, 13, 0),
    )
    timestamp = timezone.now()
    rule = NegativeMoodChangeBetweenActivitiesRule(client_id=client.id, requested_at=timestamp)
    assert rule.get_mood_diary_entries().count() == 0
    assert rule.evaluate_preconditions() is False

    # fourth activity
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 9, 30),
        activity__value="c",
        mood__value=-2,
        start_time=datetime(2023, 9, 30, 13, 0),
        end_time=datetime(2023, 9, 30, 14, 0),
    )
    timestamp = timezone.now()
    rule = NegativeMoodChangeBetweenActivitiesRule(client_id=client.id, requested_at=timestamp)
    assert rule.get_mood_diary_entries().count() == 2
    assert rule.evaluate_preconditions() is True

    # Update second activity
    new_mood = MoodFactory.create(value=-1)
    second_activity.mood = new_mood
    second_activity.save()
    timestamp = timezone.now()
    rule = NegativeMoodChangeBetweenActivitiesRule(client_id=client.id, requested_at=timestamp)
    assert rule.get_mood_diary_entries().count() == 2
    assert rule.evaluate_preconditions() is True
    assert not Notification.objects.exists()
    assert not RuleTriggeredLog.objects.exists()
    rule.evaluate()
    assert Notification.objects.count() == 1
    assert RuleTriggeredLog.objects.count() == 1


@pytest.mark.django_db
def test_daily_average_mood_improving_rule(freezer):
    freezer.move_to("2023-09-30")
    client = ClientFactory.create()
    MoodDiaryFactory.create(client=client)
    rule_db = RuleFactory.create(title="Daily average mood improving")
    rule_db.subscribed_clients.add(client)

    timestamp = timezone.now()
    rule = DailyAverageMoodImprovingRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is True
    assert rule.get_mood_diary_entries().count() == 0
    assert rule.evaluate_preconditions() is False

    # Only entries for today, not for yesterday
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 9, 30),
        mood__value=-1,
    )
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 9, 30),
        mood__value=1,
    )
    assert rule.get_mood_diary_entries().count() == 2
    assert rule.evaluate_preconditions() is False

    # Entries for today and yesterday, but no improvement
    freezer.move_to("2023-10-01")
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 10, 1),
        mood__value=-2,
    )
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 10, 1),
        mood__value=0,
    )
    timestamp = timezone.now()
    rule = DailyAverageMoodImprovingRule(client_id=client.id, requested_at=timestamp)
    assert rule.evaluate_preconditions() is False

    # Entries for today and yesterday, with improvement
    freezer.move_to("2023-10-02")
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 10, 2),
        mood__value=1,
    )
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date=date(2023, 10, 2),
        mood__value=3,
    )
    timestamp = timezone.now()
    rule = DailyAverageMoodImprovingRule(client_id=client.id, requested_at=timestamp)
    assert rule.evaluate_preconditions() is True
    assert not Notification.objects.exists()
    assert not RuleTriggeredLog.objects.exists()
    rule.evaluate()
    assert Notification.objects.count() == 1
    assert RuleTriggeredLog.objects.count() == 1
    assert rule.triggering_allowed() is False

    freezer.move_to("2023-10-03")
    timestamp = timezone.now()
    rule = DailyAverageMoodImprovingRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is True


@pytest.mark.django_db
def test_physical_activity_per_week_increasing_rule(freezer):
    freezer.move_to("2023-09-30")
    client = ClientFactory.create()
    MoodDiaryFactory.create(client=client)
    rule_db = RuleFactory.create(title="Physical activity per week increasing")
    rule_db.subscribed_clients.add(client)

    # Saturday
    timestamp = timezone.now()
    rule = PhysicalActivityPerWeekIncreasingRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is False

    # Sunday
    freezer.move_to("2023-10-01")
    timestamp = timezone.now()
    rule = PhysicalActivityPerWeekIncreasingRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is True
    assert rule.get_mood_diary_entries().count() == 0
    assert rule.evaluate_preconditions() is False

    # Some entries for the current week
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date="2023-09-26",
        activity__category__value=ActivityCategory.physical_activity_value,
        mood__value=1,
        start_time=datetime(2023, 9, 25, 12, 0),
        end_time=datetime(2023, 9, 25, 13, 0),
    )
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date="2023-09-27",
        activity__category__value=ActivityCategory.physical_activity_value,
        mood__value=1,
        start_time=datetime(2023, 9, 30, 15, 0),
        end_time=datetime(2023, 9, 30, 16, 0),
    )
    assert rule.get_mood_diary_entries().count() == 2
    assert rule.evaluate_preconditions() is False

    # Next week's sunday
    freezer.move_to("2023-10-08")
    timestamp = timezone.now()
    rule = PhysicalActivityPerWeekIncreasingRule(client_id=client.id, requested_at=timestamp)
    assert rule.triggering_allowed() is True
    assert rule.get_mood_diary_entries().count() == 2
    assert rule.evaluate_preconditions() is False

    # Some entries for the next week (same amount as this week)
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date="2023-10-06",
        activity__category__value=ActivityCategory.physical_activity_value,
        mood__value=1,
        start_time=datetime(2023, 9, 30, 12, 0),
        end_time=datetime(2023, 9, 30, 13, 0),
    )
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date="2023-10-07",
        activity__category__value=ActivityCategory.physical_activity_value,
        mood__value=1,
        start_time=datetime(2023, 9, 30, 15, 0),
        end_time=datetime(2023, 9, 30, 16, 0),
    )
    assert rule.get_mood_diary_entries().count() == 4
    assert rule.evaluate_preconditions() is False

    # Increase next week's amount
    MoodDiaryEntryFactory.create(
        mood_diary__client=client,
        date="2023-10-07",
        activity__category__value=ActivityCategory.physical_activity_value,
        mood__value=1,
        start_time=datetime(2023, 9, 30, 17, 0),
        end_time=datetime(2023, 9, 30, 18, 0),
    )
    assert rule.get_mood_diary_entries().count() == 5
    assert rule.evaluate_preconditions() is True
    assert not Notification.objects.exists()
    assert not RuleTriggeredLog.objects.exists()
    rule.evaluate()
    assert Notification.objects.count() == 1
    assert RuleTriggeredLog.objects.count() == 1
    assert rule.triggering_allowed() is False
