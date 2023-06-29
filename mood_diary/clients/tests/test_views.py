import http

import pytest
from clients.forms import ClientCreationForm
from clients.models import Client
from clients.tests.factories import ClientFactory
from diaries.models import MoodDiary, MoodDiaryEntry
from diaries.tests.factories import MoodDiaryEntryFactory
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
def counselor_with_client(create_user):
    counselor = create_user(role=User.Role.COUNSELOR)
    client = ClientFactory.create(counselor=counselor)
    return counselor, client


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
def test_mood_diary_entry_detail_client_view(counselor_with_client, create_response):
    counselor, client = counselor_with_client
    entry = MoodDiaryEntryFactory.create(mood_diary__client=client, released=True)
    url = reverse(
        "clients:get_mood_diary_entry_client", kwargs={"client_pk": client.pk, "entry_pk": entry.pk}
    )
    response = create_response(counselor, url)

    assert response.status_code == http.HTTPStatus.OK
    assert response.context_data["entry"] == entry


@pytest.mark.django_db
def test_mood_diary_entry_detail_client_view_restricted(counselor_with_client, create_response):
    counselor, client = counselor_with_client
    some_client = ClientFactory.create()
    entry_some_client = MoodDiaryEntryFactory.create(mood_diary__client=some_client)
    entry_not_released = MoodDiaryEntryFactory(mood_diary__client=client, released=False)

    # unassigned client
    url = reverse(
        "clients:get_mood_diary_entry_client",
        kwargs={"client_pk": some_client.pk, "entry_pk": entry_some_client.pk},
    )

    response = create_response(counselor, url)

    assert response.status_code == http.HTTPStatus.NOT_FOUND

    # assigned client but unassigned client's entry
    url = reverse(
        "clients:get_mood_diary_entry_client",
        kwargs={"client_pk": client.pk, "entry_pk": entry_some_client.pk},
    )

    response = create_response(counselor, url)

    assert response.status_code == http.HTTPStatus.NOT_FOUND

    # assigned client but unreleased entry
    url = reverse(
        "clients:get_mood_diary_entry_client",
        kwargs={"client_pk": client.pk, "entry_pk": entry_not_released.pk},
    )

    response = create_response(counselor, url)

    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_mood_diary_entry_list_counselor_view(counselor_with_client, create_response):
    counselor, client = counselor_with_client
    some_client = ClientFactory.create()
    MoodDiaryEntryFactory.create(mood_diary__client=some_client)
    MoodDiaryEntryFactory(mood_diary__client=client, released=False)
    entry = MoodDiaryEntryFactory(mood_diary__client=client, released=True)
    assert MoodDiaryEntry.objects.count() == 3
    url = reverse("clients:list_mood_diary_entries_client", kwargs={"client_pk": client.id})

    response = create_response(counselor, url)

    assert response.status_code == http.HTTPStatus.OK
    assert entry in (response_entries := response.context_data["entries"])
    assert response_entries.count() == 1
    assert "clients/mood_diary_entries_list.html" in response.template_name


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


@pytest.mark.django_db
def test_client_update_to_inactive_view(create_user, create_response):
    counselor = create_user(User.Role.COUNSELOR)
    client = ClientFactory.create(counselor=counselor, active=True)
    assert Client.objects.filter(active=True).count() == 1
    url = reverse("clients:update_to_inactive", kwargs={"pk": client.pk})

    response = create_response(counselor, url, method="POST")

    assert response.status_code == http.HTTPStatus.FOUND
    assert not Client.objects.filter(active=True).exists()
    assert not Client.objects.get(pk=client.pk).active

    # Client not belonging to this Counselor is not set to inactive
    client = ClientFactory.create(active=True)
    assert Client.objects.filter(active=True).count() == 1
    url = reverse("clients:update_to_inactive", kwargs={"pk": client.pk})

    response = create_response(counselor, url, method="POST")

    assert response.status_code == http.HTTPStatus.FOUND
    assert Client.objects.filter(active=True).count() == 1
