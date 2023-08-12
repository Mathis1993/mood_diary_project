from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions
from notifications.models import Notification


@register(Notification)
class NotificationTranslationOptions(TranslationOptions):
    """
    This class is used to translate the Notification model.
    """

    fields = ("message",)
