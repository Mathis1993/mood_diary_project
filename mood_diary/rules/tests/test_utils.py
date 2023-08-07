from datetime import datetime

from django.utils import timezone
from rules.utils import get_beginning_of_week, get_end_of_week


def test_get_beginning_of_current_week(freezer):
    freezer.move_to("2023-09-27 00:00:00")
    beginning_of_week = get_beginning_of_week()
    assert beginning_of_week == datetime(2023, 9, 25, 0, 0, 0, tzinfo=timezone.utc)

    freezer.move_to("2023-10-01 23:59:59")
    beginning_of_week = get_beginning_of_week()
    assert beginning_of_week == datetime(2023, 9, 25, 0, 0, 0, tzinfo=timezone.utc)

    freezer.move_to("2023-10-02 00:00:00")
    beginning_of_week = get_beginning_of_week()
    assert beginning_of_week == datetime(2023, 10, 2, 0, 0, 0, tzinfo=timezone.utc)

    beginning_of_week = get_beginning_of_week(datetime(2023, 8, 30, 0, 0, 0, tzinfo=timezone.utc))
    assert beginning_of_week == datetime(2023, 8, 28, 0, 0, 0, tzinfo=timezone.utc)


def test_get_end_of_current_week(freezer):
    freezer.move_to("2023-09-27 00:00:00")
    end_of_week = get_end_of_week()
    assert end_of_week == datetime(2023, 10, 1, 23, 59, 59, 999999, tzinfo=timezone.utc)

    freezer.move_to("2023-10-01 23:59:59")
    end_of_week = get_end_of_week()
    assert end_of_week == datetime(2023, 10, 1, 23, 59, 59, 999999, tzinfo=timezone.utc)

    freezer.move_to("2023-10-02 00:00:00")
    end_of_week = get_end_of_week()
    assert end_of_week == datetime(2023, 10, 8, 23, 59, 59, 999999, tzinfo=timezone.utc)

    end_of_week = get_end_of_week(datetime(2023, 8, 30, 0, 0, 0, tzinfo=timezone.utc))
    assert end_of_week == datetime(2023, 9, 3, 23, 59, 59, 999999, tzinfo=timezone.utc)
