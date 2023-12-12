import http
import json

import pytest
from clients.tests.factories import ClientFactory
from notifications.models import PushSubscription
from notifications.tests.factories import PushSubscriptionFactory
from pytest_mock import MockerFixture
from pywebpush import WebPushException


@pytest.mark.django_db
def test_push_subscription_send_push_notification(mocker: MockerFixture):
    mocked_function = mocker.patch("notifications.models.webpush")

    client = ClientFactory.create()
    subscription = PushSubscriptionFactory.create(client=client)
    subscription.send_push_notification({"test": "test"})
    assert mocked_function.call_count == 1
    assert mocked_function.call_args[1]["subscription_info"] == subscription.subscription
    assert mocked_function.call_args[1]["data"] == json.dumps({"test": "test"})


@pytest.mark.django_db
def test_push_subscription_send_push_notification_fails_invalid_subscription(mocker: MockerFixture):
    class WebPushResponse:
        status_code = http.HTTPStatus.GONE

    web_push_exception = WebPushException("error", response=WebPushResponse())
    mocked_function = mocker.patch("notifications.models.webpush", side_effect=web_push_exception)

    client = ClientFactory.create()
    subscription = PushSubscriptionFactory.create(client=client)
    subscription.send_push_notification({"test": "test"})
    assert mocked_function.call_count == 1
    # Invalid subscription, so it should be deleted
    assert PushSubscription.objects.exists() is False


@pytest.mark.django_db
def test_push_subscription_send_push_notification_fails_other(mocker: MockerFixture):
    class WebPushResponse:
        status_code = http.HTTPStatus.IM_A_TEAPOT

    web_push_exception = WebPushException("error", response=WebPushResponse())
    mocked_function = mocker.patch("notifications.models.webpush", side_effect=web_push_exception)

    client = ClientFactory.create()
    subscription = PushSubscriptionFactory.create(client=client)
    with pytest.raises(WebPushException):
        subscription.send_push_notification({"test": "test"})

    assert mocked_function.call_count == 1
