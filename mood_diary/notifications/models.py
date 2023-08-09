from core.models import TrackCreationAndUpdates
from django.db import models


class Notification(TrackCreationAndUpdates):
    class Meta:
        db_table = "notifications_notifications"
        ordering = ["viewed", "-created_at"]

    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.TextField()
    viewed = models.BooleanField(default=False)
    rule = models.ForeignKey(
        "rules.Rule",
        on_delete=models.RESTRICT,
        related_name="notifications",
    )
