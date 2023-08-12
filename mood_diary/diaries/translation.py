from diaries.models import Activity, ActivityCategory, Mood
from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions


@register(Mood)
class MoodTranslationOptions(TranslationOptions):
    """
    This class is used to translate the Mood model.
    """

    fields = ("label",)


@register(Activity)
class ActivityTranslationOptions(TranslationOptions):
    """
    This class is used to translate the Activity model.
    """

    fields = ("value",)


@register(ActivityCategory)
class ActivityCategoryTranslationOptions(TranslationOptions):
    """
    This class is used to translate the ActivityCategory model.
    """

    fields = ("value",)
