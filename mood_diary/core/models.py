from django.db import models


class TrackCreation(models.Model):
    """
    Abstract model that tracks the creation date of a model instance.
    """

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class TrackUpdates(models.Model):
    """
    Abstract model that tracks the last update date of a model instance.
    """

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TrackCreationAndUpdates(TrackCreation, TrackUpdates):
    """
    Abstract model that tracks the creation and last update date of a model instance.
    """

    class Meta:
        abstract = True


class NormalizedStringValueModel(models.Model):
    """
    Abstract model that stores a normalized string value.
    """

    value = models.CharField(max_length=255)

    class Meta:
        abstract = True


class NormalizedScaleModel(models.Model):
    """
    Abstract model that stores a normalized scale value.
    """

    label = models.CharField(max_length=255)
    value = models.IntegerField()

    class Meta:
        abstract = True
