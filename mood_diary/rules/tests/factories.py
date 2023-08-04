from datetime import timedelta

import factory.fuzzy
from django.utils import timezone
from rules.models import Rule, RuleClient, RuleTriggeredLog

RULE_TITLES = [
    "Activity with peak mood",
    "Relaxing activity",
    "Physical activity per week",
    "High media usage per day",
    "Low media usage per day",
    "14 day mood average",
    "14 day mood maximum",
    "Unsteady food intake",
    "Positive mood change between activities",
    "Negative mood change between activities",
    "Daily mean mood improving",
    "Physical activity per week increasing",
]


class RuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rule
        django_get_or_create = ("title",)

    title = factory.fuzzy.FuzzyChoice(RULE_TITLES)
    preconditions_description = factory.fuzzy.FuzzyText(length=20)
    criterion = factory.fuzzy.FuzzyChoice(Rule.Criterion.choices)
    evaluation = factory.fuzzy.FuzzyChoice(Rule.Evaluation.choices)
    conclusion_message = factory.fuzzy.FuzzyText(length=100)


class RuleClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RuleClient
        django_get_or_create = ("rule", "client")

    rule = factory.SubFactory(RuleFactory)
    user = factory.SubFactory("clients.tests.factories.ClientFactory")


class RuleTriggeredLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RuleTriggeredLog

    rule = factory.SubFactory(RuleFactory)
    client = factory.SubFactory("clients.tests.factories.ClientFactory")
    created_at = factory.fuzzy.FuzzyDateTime(start_dt=timezone.now() - timedelta(days=30))
