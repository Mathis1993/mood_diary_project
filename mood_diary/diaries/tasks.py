import logging
from datetime import timedelta

from celery import shared_task
from clients.models import Client
from django.utils import timezone
from rules.rules import EVENT_BASED_RULES, TIME_BASED_RULES
from rules.utils import RuleMessage

logger = logging.getLogger("mood_diary.diaries.tasks")


@shared_task
def task_event_based_rules_evaluation(msg: RuleMessage):
    """
    Task to evaluate event-based rules for a client.

    Parameters
    ----------
    msg: RuleMessage
        Holding a timestamp at which rule evaluation was requested and a client id.

    Returns
    -------
    None
    """
    logger.info(f"Event-based Rule Evaluation: {msg}")
    for rule_class in EVENT_BASED_RULES:
        rule = rule_class(*msg)
        rule.evaluate()


@shared_task
def task_time_based_rules_init():
    """
    Task to initialize the evaluation of event-based rules for all clients.
    This task will run daily at 6 am, setting the timestamp for rule evaluation
    to the previous day at 23:59:59.

    Returns
    -------
    None
    """
    for client in Client.objects.filter(active=True):
        timestamp = (timezone.now() - timedelta(days=1)).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        msg = RuleMessage(client.id, timestamp)
        task_time_based_rules_evaluation.delay(msg)


@shared_task
def task_time_based_rules_evaluation(msg: RuleMessage):
    """
    Task to evaluate time-based rules for a client.

    Parameters
    ----------
    msg: RuleMessage
        Holding a timestamp at which rule evaluation was requested and a client id.

    Returns
    -------
    None
    """
    logger.info(f"Time-based Rule Evaluation: {msg}")
    for rule_class in TIME_BASED_RULES:
        rule = rule_class(*msg)
        rule.evaluate()
