import pytest
from clients.models import Client
from clients.tests.factories import ClientFactory
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from notifications.tests.factories import NotificationFactory
from users.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
def test_client_unique():
    counselor = UserFactory.create(role=User.Role.COUNSELOR)
    client_user = UserFactory.create(role=User.Role.CLIENT)

    # The client_user must be unique
    Client.objects.create(user=client_user, identifier="client1", counselor=counselor, active=True)
    with pytest.raises(IntegrityError):
        Client.objects.create(
            user=client_user, identifier="client2", counselor=counselor, active=True
        )


@pytest.mark.django_db
def test_client_save_validation():
    counselor = UserFactory.create(role=User.Role.COUNSELOR)
    client_user = UserFactory.create(role=User.Role.CLIENT)

    # Valid user and counselor role
    client = Client(user=client_user, identifier="client1", counselor=counselor, active=True)
    client.save()

    # Invalid user role
    client.user = counselor
    with pytest.raises(IntegrityError):
        client.save()

    # Invalid counselor role
    client.user = client_user
    client.counselor = client_user
    with pytest.raises(IntegrityError):
        client.save()


@pytest.mark.django_db
def test_client_new_notifications_count():
    user = UserFactory.create(role=User.Role.CLIENT)
    counselor = UserFactory.create(role=User.Role.COUNSELOR)
    client = Client.objects.create(user=user, counselor=counselor, identifier="test123")

    NotificationFactory.create(client=client, viewed=False)
    NotificationFactory.create(client=client, viewed=False)
    NotificationFactory.create(client=client, viewed=True)  # This one is viewed

    assert client.new_notifications_count() == 2


@pytest.mark.django_db
def test_get_newest_notifications():
    user = UserFactory(role=User.Role.CLIENT)
    counselor = UserFactory(role=User.Role.COUNSELOR)
    client = Client.objects.create(user=user, counselor=counselor, identifier="test123")

    NotificationFactory.create(client=client, viewed=False)
    NotificationFactory.create(client=client, viewed=True)
    notif_2 = NotificationFactory.create(client=client, viewed=False)
    notif_3 = NotificationFactory.create(client=client, viewed=False)
    notif_4 = NotificationFactory.create(client=client, viewed=False)
    NotificationFactory.create(client=client, viewed=True)

    newest_notifications = client.get_newest_notifications()
    assert len(newest_notifications) == 3
    assert notif_4 in newest_notifications
    assert notif_3 in newest_notifications
    assert notif_2 in newest_notifications


@pytest.mark.django_db
def test_client_ask_for_push_notifications_permission():
    client = ClientFactory.create(push_notifications_granted=None)
    assert client.ask_for_push_notifications_permission() is True

    client.push_notifications_granted = True
    client.save()

    assert client.ask_for_push_notifications_permission() is False

    client.push_notifications_granted = False
    client.save()

    assert client.ask_for_push_notifications_permission() is False
