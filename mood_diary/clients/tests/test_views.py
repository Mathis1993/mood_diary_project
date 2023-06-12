import http

import pytest
from clients.forms import ClientCreationForm
from clients.models import Client
from clients.tests.factories import ClientFactory
from diaries.models import MoodDiary
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.tests.factories import UserFactory

User = get_user_model()


@pytest.fixture
def create_user():
    def _create_user(role):
        return UserFactory.create(role=role)

    return _create_user


@pytest.mark.django_db
def test_create_client_view_get(create_user, create_response):
    counselor = create_user(User.Role.COUNSELOR)
    url = reverse("clients:create_client")

    response = create_response(user=counselor, url=url)

    assert response.status_code == http.HTTPStatus.OK
    assert isinstance(response.context["form"], ClientCreationForm)


@pytest.mark.django_db
def test_create_client_view_post_valid_form(create_user, create_response):
    counselor = create_user(User.Role.COUNSELOR)
    url = reverse("clients:create_client")

    response = create_response(
        user=counselor,
        url=url,
        method="POST",
        data={"email": "test@example.com", "identifier": "client1"},
    )

    assert response.status_code == http.HTTPStatus.OK
    assert "email" in response.context
    assert "password" in response.context
    assert User.objects.filter(email="test@example.com", role=User.Role.CLIENT).exists()
    assert Client.objects.filter(identifier="client1", counselor=counselor).exists()
    assert MoodDiary.objects.filter(client__identifier="client1").exists()


@pytest.mark.django_db
def test_create_client_view_post_invalid_email(create_user, create_response):
    counselor = create_user(User.Role.COUNSELOR)
    url = reverse("clients:create_client")

    response = create_response(
        user=counselor,
        url=url,
        method="POST",
        data={"email": "invalid-email", "identifier": "client1"},
    )

    assert response.status_code == http.HTTPStatus.OK
    assert isinstance(response.context["form"], ClientCreationForm)
    assert "email" in response.context["form"].errors


@pytest.mark.django_db
def test_create_client_view_post_client_already_exists(create_user, create_response):
    counselor = create_user(User.Role.COUNSELOR)
    ClientFactory.create(user__email="test@example.com")
    url = reverse("clients:create_client")

    response = create_response(
        user=counselor,
        url=url,
        method="POST",
        data={"email": "test@example.com", "identifier": "client1"},
    )

    assert response.status_code == http.HTTPStatus.OK
    assert isinstance(response.context["form"], ClientCreationForm)
    assert "email" in response.context["form"].errors


@pytest.mark.django_db
def test_create_client_view_permission(create_user, create_response):
    client_user = create_user(User.Role.CLIENT)
    url = reverse("clients:create_client")

    response = create_response(user=client_user, url=url)

    assert response.status_code == http.HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_client_list_view(create_user, create_response):
    counselor = create_user(User.Role.COUNSELOR)
    client = ClientFactory.create(counselor=counselor)
    ClientFactory.create()
    assert Client.objects.count() == 2
    url = reverse("clients:list_clients")

    response = create_response(counselor, url)

    assert response.status_code == http.HTTPStatus.OK
    assert client in (response_clients := response.context_data["clients"])
    assert response_clients.count() == 1
    assert "clients/clients_list.html" in response.template_name
