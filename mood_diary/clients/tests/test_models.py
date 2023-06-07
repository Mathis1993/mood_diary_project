import pytest
from clients.models import Client
from django.contrib.auth import get_user_model
from django.db import IntegrityError
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
