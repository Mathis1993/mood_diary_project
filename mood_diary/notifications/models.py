import http

from core.models import TrackCreationAndUpdates
from django.conf import settings
from django.db import models
from pywebpush import WebPusher, WebPushException


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


class PushSubscription(TrackCreationAndUpdates):
    class Meta:
        db_table = "notifications_push_subscriptions"

    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="push_subscriptions",
    )
    subscription = models.JSONField()

    def send_push_notification(self, message):
        pusher = WebPusher(self.subscription)
        try:
            pusher.send(message, ttl=settings.WEB_PUSH_TTL)
        except WebPushException as e:
            # If the subscription is expired or no longer valid, delete it
            if e.response.status_code == http.HTTPStatus.GONE:
                self.delete()
            else:
                # ToDo(ME-17.08.23): Log error, sth else here?
                raise e
