import factory.fuzzy
from django.utils import timezone
from rules.content.rules import RULE_TITLES_CONCLUSION_MESSAGES_EN_DE, RULE_TITLES_EN_DE
from rules.models import Rule, RuleClient, RuleTriggeredLog


class RuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rule
        django_get_or_create = ("title",)

    title = factory.fuzzy.FuzzyChoice(list(RULE_TITLES_EN_DE.keys()))
    preconditions_description = factory.fuzzy.FuzzyText(length=20)
    criterion = factory.fuzzy.FuzzyChoice(Rule.Criterion.choices)
    evaluation = factory.fuzzy.FuzzyChoice(Rule.Evaluation.choices)
    conclusion_message = factory.LazyAttribute(
        lambda obj: RULE_TITLES_CONCLUSION_MESSAGES_EN_DE[obj.title]["en"]
    )


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
