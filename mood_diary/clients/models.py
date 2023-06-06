from core.models import TrackCreationAndUpdates
from django.conf import settings
from django.db import models


class Client(TrackCreationAndUpdates):
    class Meta:
        db_table = "clients_clients"
        unique_together = ["identifier", "counselor"]

    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user"
    )
    identifier = models.CharField(max_length=255)
    counselor = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name="counselor"
    )
    active = models.BooleanField(default=True)
