from core.models import TrackCreationAndUpdates
from django.db import models


class Notification(TrackCreationAndUpdates):
    class Meta:
        db_table = "notifications_notifications"

    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.TextField()
    viewed = models.BooleanField(default=False)
