import http

import pytest
from clients.tests.factories import ClientFactory
from django.urls import reverse
from notifications.models import Notification
from notifications.tests.factories import NotificationFactory


@pytest.mark.django_db
def test_mood_diary_entry_detail_view(user, create_response):
    notification = NotificationFactory.create(client=user.client)
    url = reverse("notifications:get_notification", kwargs={"pk": notification.pk})
    response = create_response(user, url)

    assert response.status_code == http.HTTPStatus.OK
    assert response.context_data["notification"] == notification


@pytest.mark.django_db
def test_mood_diary_entry_detail_view_restricted(user, create_response):
    other_client = ClientFactory.create()
    notification = NotificationFactory.create(client=user.client)
    url = reverse("notifications:get_notification", kwargs={"pk": notification.pk})

    response = create_response(other_client.user, url)

    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_mood_diary_entry_list_view(user, create_response):
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
