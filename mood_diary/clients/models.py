from core.models import TrackCreationAndUpdates
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, models

User = get_user_model()


class Client(TrackCreationAndUpdates):
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

    def save(self, *args, **kwargs):
        """
        Validate user roles.
        """
        if not self.user.role == User.Role.CLIENT:
            raise IntegrityError("The client user must have the client role")

        if not self.counselor.role == User.Role.COUNSELOR:
            raise IntegrityError("The counselor user must have the counselor role")

        super().save(*args, **kwargs)

    def new_notifications_count(self):
        return self.notifications.filter(viewed=False).count()

    def get_newest_notifications(self):
        return self.notifications.filter(viewed=False).all()[:3]
