from datetime import timedelta
from typing import NamedTuple

from django.utils import timezone


def get_beginning_of_week(today: timezone.datetime = None) -> timezone.datetime:
    """
    Returns timestamp of the Monday of the current week at 00:00:00.
    """
    today = today or timezone.now()
    monday = today - timedelta(days=today.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def get_end_of_week(today: timezone.datetime = None) -> timezone.datetime:
    """
    Returns timestamp of the Sunday of the current week at 23:59:59.
    """
    today = today or timezone.now()
    monday = today + timedelta(days=7 - today.weekday() - 1)
    return monday.replace(hour=23, minute=59, second=59, microsecond=999999)


class RuleMessage(NamedTuple):
    """
    An object bundling all information passed around
    during asynchronous task processing for rules."""

    client_id: int
    timestamp: timezone.datetime

    def __str__(self):
        return f"Client {self.client_id} - {self.timestamp}"
