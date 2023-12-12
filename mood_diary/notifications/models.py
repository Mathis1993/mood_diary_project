import http
import json
import logging

from core.models import TrackCreationAndUpdates
from django.conf import settings
from django.db import models
from pywebpush import WebPushException, webpush


class Notification(TrackCreationAndUpdates):
    """
    This is the Notification model representing a notification for a client.
    """

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
    """
    This is the PushSubscription model representing a push subscription for a client
    with all information necessary for that held in a json field.
    """

    class Meta:
        db_table = "notifications_push_subscriptions"

    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="push_subscriptions",
    )
    subscription = models.JSONField()

    logger = logging.getLogger("notifications.models.PushSubscription")

    def send_push_notification(self, message: dict):
        """
        Send a push notification using the subscription the current model instance holds.
        The message that is sent is encrypted via the VAPID protocol so that the push
        service cannot access it.

        Parameters
        ----------
        message: dict
            The push notification content.

        Returns
        -------
        None

        Raises
        ------
        WebPushException
        """
        self.logger.info(f"Trying to send push notification to {self.client.identifier}")
        try:
            webpush(
                subscription_info=self.subscription,
                data=json.dumps(message),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": "mailto:info@mood-diary.de",
                },
                ttl=settings.WEB_PUSH_TTL,
            )
            self.logger.info(f"Successfully sent push notification to {self.client.identifier}")
        except WebPushException as e:
            self.logger.error(f"Error sending push notification to {self.client.identifier}")
            self.logger.error(e)
            # If the subscription is expired or no longer valid, delete it
            if e.response.status_code == http.HTTPStatus.GONE:
                self.delete()
            else:
                raise e
