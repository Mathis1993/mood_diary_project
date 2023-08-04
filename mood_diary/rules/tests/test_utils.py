from datetime import datetime

from django.utils import timezone
from rules.utils import get_beginning_of_current_week


def test_get_beginning_of_current_week(freezer):
    freezer.move_to("2023-09-27 00:00:00")
    beginning_of_week = get_beginning_of_current_week()
    assert beginning_of_week == datetime(2023, 9, 25, 0, 0, 0, tzinfo=timezone.utc)

    freezer.move_to("2023-10-01 23:59:59")
    beginning_of_week = get_beginning_of_current_week()
    assert beginning_of_week == datetime(2023, 9, 25, 0, 0, 0, tzinfo=timezone.utc)

    freezer.move_to("2023-10-02 00:00:00")
    beginning_of_week = get_beginning_of_current_week()
    assert beginning_of_week == datetime(2023, 10, 2, 0, 0, 0, tzinfo=timezone.utc)
