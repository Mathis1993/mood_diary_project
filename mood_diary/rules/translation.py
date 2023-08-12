from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions
from rules.models import Rule


@register(Rule)
class RuleTranslationOptions(TranslationOptions):
    """
    This class is used to translate the Rule model.
    """

    fields = ("title", "conclusion_message")
