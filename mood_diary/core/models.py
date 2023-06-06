from django.db import models


class TrackCreation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class TrackUpdates(models.Model):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TrackCreationAndUpdates(TrackCreation, TrackUpdates):
    class Meta:
        abstract = True
