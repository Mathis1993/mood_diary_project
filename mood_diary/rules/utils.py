from datetime import timedelta

from django.utils import timezone


def get_beginning_of_week(today: timezone.datetime = None) -> timezone.datetime:
    """
    Returns timestamp of the Monday of the current week at 00:00:00.
    """
    today = today or timezone.now()
    monday = today - timedelta(days=today.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)
