from core.models import TrackCreationAndUpdates
from django.conf import settings
from django.db import models


class Notification(TrackCreationAndUpdates):
    class Meta:
        db_table = "notifications_notifications"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.TextField()
    viewed = models.BooleanField(default=False)
