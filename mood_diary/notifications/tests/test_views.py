import http
import json

import pytest
from clients.tests.factories import ClientFactory
from django.urls import reverse
from notifications.models import Notification
from notifications.tests.factories import NotificationFactory


@pytest.mark.django_db
def test_notification_detail_view(user, create_response):
    notification = NotificationFactory.create(client=user.client)
    url = reverse("notifications:get_notification", kwargs={"pk": notification.pk})
    response = create_response(user, url)

    assert response.status_code == http.HTTPStatus.OK
    assert response.context_data["notification"] == notification


@pytest.mark.django_db
def test_notification_detail_view_restricted(user, create_response):
    other_client = ClientFactory.create()
    notification = NotificationFactory.create(client=user.client)
    url = reverse("notifications:get_notification", kwargs={"pk": notification.pk})

    response = create_response(other_client.user, url)

    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_notification_list_view(user, create_response):
    notification = NotificationFactory.create(client=user.client)
    other_client = ClientFactory.create()
    NotificationFactory.create(client=other_client)
    assert Notification.objects.count() == 2
    url = reverse("notifications:get_all_notifications")

    response = create_response(user, url)

    assert response.status_code == http.HTTPStatus.OK
    assert notification in (response_entries := response.context_data["notifications"])
    assert response_entries.count() == 1
    assert "notifications/notification_list.html" in response.template_name


@pytest.mark.django_db
def test_update_notifications_permission_view(user, create_response):
    assert user.client.push_notifications_granted is None
    url = reverse("notifications:update_notifications_permission")
    data = {"permission": "granted"}
    data_json = json.dumps(data)

    response = create_response(
        user, url, method="POST", data=data_json, content_type="application/json"
    )

    assert response.status_code == http.HTTPStatus.OK
    user.client.refresh_from_db()
    assert user.client.push_notifications_granted is True

    data["permission"] = "denied"
    data_json = json.dumps(data)
    response = create_response(
        user, url, method="POST", data=data_json, content_type="application/json"
    )

    assert response.status_code == http.HTTPStatus.OK
    user.client.refresh_from_db()
    assert user.client.push_notifications_granted is False


@pytest.mark.django_db
def test_push_subscription_create_view(user, create_response):
    url = reverse("notifications:create_push_subscription")
    subscription = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/c-g36SB-_FU:APA91bFVHgwBE7Qw81RgXU6SXZ2pRlW1SV44s1oUMI9FX8JT-uCTJAJDD1jCvyYVYofbVcQG2f9CNqo1ujenI6BMiomelh5pO-MBFVE8bInFb9c9bbj8AlWMPiTrmb6oGkE6sMqIawIS",  # noqa E501
        "expirationTime": "null",
        "keys": {
            "p256dh": "BKbfcPS4ivMtp-zpVqyIQI60M5RLlol8582AhDl9V6TukmEiWzAbjrrLRPhHmoyHhbsrhRkdAXa7Sfe13aNrurQ",  # noqa E501
            "auth": "Stn8bCwWxn7CLiR_2hLeDA",
        },
    }
    data = subscription
    data_json = json.dumps(data)

    response = create_response(
        user, url, method="POST", data=data_json, content_type="application/json"
    )

    assert response.status_code == http.HTTPStatus.CREATED
    assert user.client.push_subscriptions.count() == 1
    assert user.client.push_subscriptions.first().subscription == subscription

    response = create_response(
        user, url, method="POST", data=data_json, content_type="application/json"
    )

    assert response.status_code == http.HTTPStatus.OK
    assert user.client.push_subscriptions.count() == 1
