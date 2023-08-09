from core.models import TrackCreation, TrackCreationAndUpdates
from django.db import models


class Rule(TrackCreationAndUpdates):
    class Meta:
        db_table = "rules_rules"
        ordering = ["title"]

    class Criterion(models.TextChoices):
        THRESHOLD = "threshold"
        CHANGE = "change"

    class Evaluation(models.TextChoices):
        EVENT_BASED = "event-based"
        TIME_BASED = "time-based"

    title = models.CharField(max_length=255, unique=True)
    preconditions_description = models.TextField()
    criterion = models.TextField(choices=Criterion.choices, max_length=255)
    evaluation = models.TextField(choices=Evaluation.choices, max_length=255)
    conclusion_message = models.TextField()
    subscribed_clients = models.ManyToManyField(
        through="RuleClient", to="clients.Client", related_name="subscribed_rules"
    )


class RuleClient(TrackCreationAndUpdates):
    class Meta:
        db_table = "rules_rules_clients"
        ordering = ["-active", "rule__title"]

    rule = models.ForeignKey(Rule, on_delete=models.RESTRICT, related_name="rule_users")
    client = models.ForeignKey(
        "clients.Client", on_delete=models.CASCADE, related_name="rule_users"
    )
    active = models.BooleanField(default=True)


class RuleTriggeredLog(TrackCreation):
    class Meta:
        db_table = "rules_triggered_logs"

    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name="triggered_logs")
    client = models.ForeignKey(
        "clients.Client", on_delete=models.CASCADE, related_name="rules_triggered_logs"
    )
