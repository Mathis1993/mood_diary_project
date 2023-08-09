import pytest
from clients.tests.factories import ClientFactory
from diaries.tasks import task_event_based_rules_evaluation, task_time_based_rules_init
from django.utils import timezone
from pytest_mock import MockerFixture
from rules.rules import EVENT_BASED_RULES, TIME_BASED_RULES
from rules.utils import RuleMessage


def test_task_event_based_rules_evaluation(mocker: MockerFixture):
    mocked_method = mocker.patch("rules.rules.BaseRule.evaluate")
    rule_message = RuleMessage(client_id=1, timestamp=timezone.now())
    task_event_based_rules_evaluation(rule_message)
    assert mocked_method.call_count == len(EVENT_BASED_RULES)


@pytest.mark.django_db
def test_task_time_based_rules_init(mocker: MockerFixture, freezer):
    freezer.move_to("2023-10-01 06:00:00")
    mocked_method = mocker.patch("diaries.tasks.task_time_based_rules_evaluation.delay")
    ClientFactory.create_batch(size=2, active=True)
    task_time_based_rules_init()
    assert mocked_method.call_count == 2
    assert mocked_method.call_args_list[0][0][0].timestamp == timezone.datetime(
        2023, 9, 30, 23, 59, 59, 999999
    )
    assert mocked_method.call_args_list[1][0][0].timestamp == timezone.datetime(
        2023, 9, 30, 23, 59, 59, 999999
    )


def test_task_time_based_rules_evaluation(mocker: MockerFixture):
    mocked_method = mocker.patch("rules.rules.BaseRule.evaluate")
    rule_message = RuleMessage(client_id=1, timestamp=timezone.now())
    task_event_based_rules_evaluation(rule_message)
    assert mocked_method.call_count == len(TIME_BASED_RULES)
