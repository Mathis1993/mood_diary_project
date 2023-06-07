import pytest
from clients.forms import ClientCreationForm
from clients.models import Client
from clients.tests.factories import ClientFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.tests.factories import UserFactory

User = get_user_model()


@pytest.fixture
def create_user():
    def _create_user(role):
        return UserFactory.create(role=role)

    return _create_user


@pytest.fixture
def create_response(client):
    def _create_response(user, method="GET", data=None):
        client.force_login(user)
        response = getattr(client, method.lower())(reverse("clients:create_client"), data)
        return response

    return _create_response


@pytest.mark.django_db
def test_create_client_view_get(create_user, create_response):
    counselor = create_user(User.Role.COUNSELOR)
    response = create_response(user=counselor, method="GET")

    assert response.status_code == 200
    assert isinstance(response.context["form"], ClientCreationForm)


@pytest.mark.django_db
def test_create_client_view_post_valid_form(create_user, create_response):
    counselor = create_user(User.Role.COUNSELOR)
    response = create_response(
        user=counselor, method="POST", data={"email": "test@example.com", "identifier": "client1"}
    )

    assert response.status_code == 200
    assert "email" in response.context
    assert "password" in response.context
    assert User.objects.filter(email="test@example.com", role=User.Role.CLIENT).exists()
    assert Client.objects.filter(identifier="client1", counselor=counselor).exists()


@pytest.mark.django_db
def test_create_client_view_post_invalid_email(create_user, create_response):
    counselor = create_user(User.Role.COUNSELOR)
    response = create_response(
        user=counselor, method="POST", data={"email": "invalid-email", "identifier": "client1"}
    )

    assert response.status_code == 200
    assert isinstance(response.context["form"], ClientCreationForm)
    assert "email" in response.context["form"].errors


@pytest.mark.django_db
def test_create_client_view_post_client_already_exists(create_user, create_response):
    counselor = create_user(User.Role.COUNSELOR)
    ClientFactory.create(user__email="test@example.com")
    response = create_response(
        user=counselor, method="POST", data={"email": "test@example.com", "identifier": "client1"}
    )

    assert response.status_code == 200
    assert isinstance(response.context["form"], ClientCreationForm)
    assert "email" in response.context["form"].errors


@pytest.mark.django_db
def test_create_client_view_permission(create_user, create_response):
    client_user = create_user(User.Role.CLIENT)

    response = create_response(user=client_user)

    assert response.status_code == 403
