import factory.fuzzy
from django.utils import timezone
from rules.models import Rule, RuleClient, RuleTriggeredLog

RULE_TITLES_EN_DE = {
    "Activity with peak mood": "Aktivität mit maximaler Stummung",
    "Relaxing activity": "Entspannende Aktivität",
    "Physical activity per week": "Bewegung in einer Woche",
    "High media usage per day": "Hohe tägliche Mediennutzung",
    "Low media usage per day": "Geringe tägliche Mediennutzung",
    "14 day mood average": "14-Tage-Stimmungsdurchschnitt",
    "14 day mood maximum": "14-Tage-Stimmungshöchstwert",
    "Unsteady food intake": "Unregelmäßige Nahrungsaufnahme",
    "Positive mood change between activities": "Positive Stimmungsänderung zwischen Aktivitäten",
    "Negative mood change between activities": "Negative Stimmungsänderung zwischen Aktivitäten",
    "Daily average mood improving": "Verbesserung der durschn. Tagesstimmung",
    "Physical activity per week increasing": "Mehr Bewegung in einer Woche",
}


class RuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rule
        django_get_or_create = ("title",)

    title = factory.fuzzy.FuzzyChoice(list(RULE_TITLES_EN_DE.keys()))
    preconditions_description = factory.fuzzy.FuzzyText(length=20)
    criterion = factory.fuzzy.FuzzyChoice(Rule.Criterion.choices)
    evaluation = factory.fuzzy.FuzzyChoice(Rule.Evaluation.choices)
    conclusion_message = factory.fuzzy.FuzzyText(length=100)


class RuleClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RuleClient
        django_get_or_create = ("rule", "client")

    rule = factory.SubFactory(RuleFactory)
    client = factory.SubFactory("clients.tests.factories.ClientFactory")
    active = True


class RuleTriggeredLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RuleTriggeredLog

    rule = factory.SubFactory(RuleFactory)
    client = factory.SubFactory("clients.tests.factories.ClientFactory")
    requested_at = timezone.now
