from core.models import TrackCreationAndUpdates
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, models

User = get_user_model()


class Client(TrackCreationAndUpdates):
    """
    This is the Client model, representing a client executing the mood diary intervention.
    """

    class Meta:
        db_table = "clients_clients"

    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="client"
    )
    identifier = models.CharField(max_length=255)
    counselor = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name="clients"
    )
    active = models.BooleanField(default=True)
    push_notifications_granted = models.BooleanField(null=True, blank=True, default=None)
    # client_key is stored encrypted with the counselor user so that the counselor
    # can decrypt the information from mood diary entries' detail fields for their clients
    # It is encrypted with the counselor's key composed of the counselor's email address,
    # their user_id and the secret_key from the settings
    client_key_encrypted = models.TextField()

    def save(self, *args, **kwargs):
        """
        Validate user roles before saving.
        """
        if not self.user.is_client():
            raise IntegrityError("The client user must have the client role")

        if not self.counselor.is_counselor():
            raise IntegrityError("The counselor user must have the counselor role")

        super().save(*args, **kwargs)

    def new_notifications_count(self) -> int:
        """
        Calculate the current number of unread notifications.

        Returns
        -------
        int
        """
        return self.notifications.filter(viewed=False).count()

    def get_newest_notifications(self) -> models.QuerySet:
        """
        Return up to 3 of the newest unread notifications.

        Returns
        -------
        QuerySet
            Up to 3 Notification entities
        """
        return self.notifications.filter(viewed=False).all()[:3]

    def ask_for_push_notifications_permission(self) -> bool:
        """
        Return whether the client has been asked for push notification permissions
        (if not, the corresponding field is None).

        Returns
        -------
        bool
        """
        return self.push_notifications_granted is None
