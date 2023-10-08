import http

import pytest
from clients.tests.factories import ClientFactory
from core.utils import hash_email
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
def test_index_with_first_login_not_completed(client):
    user = UserFactory.create(role=User.Role.CLIENT, first_login_completed=False)
    client.force_login(user)
    url = reverse("users:index")

    response = client.get(url)

    assert response.status_code == http.HTTPStatus.FOUND
    assert response.url == reverse("users:change_password")


@pytest.mark.django_db
def test_index_with_first_login_not_completed_superuser(admin_client):
    url = reverse("users:index")

    response = admin_client.get(url)
    assert response.status_code == http.HTTPStatus.FOUND
    assert response.url == reverse("admin:index")


@pytest.mark.django_db
def test_index_with_first_login_completed_counselor(client):
    user = UserFactory.create(role=User.Role.COUNSELOR, first_login_completed=True)
    client.force_login(user)
    url = reverse("users:index")

    response = client.get(url)

    assert response.status_code == http.HTTPStatus.FOUND
    assert response.url == reverse("clients:list_clients")


@pytest.mark.django_db
def test_index_with_first_login_completed_client(client):
    user = UserFactory.create(role=User.Role.CLIENT, first_login_completed=True)
    client.force_login(user)
    url = reverse("users:index")

    response = client.get(url)

    assert response.status_code == http.HTTPStatus.FOUND
    assert response.url == reverse("dashboards:dashboard_client")


@pytest.mark.django_db
def test_custom_password_change_view_invalid_form_submission(client):
    user = UserFactory.create(role=User.Role.CLIENT, first_login_completed=False)
    client.force_login(user)
    url = reverse("users:change_password")

    response = client.post(url)

    assert response.status_code == http.HTTPStatus.OK
    user.refresh_from_db()
    assert user.first_login_completed is False


@pytest.mark.django_db
def test_custom_password_change_view_valid_form_submission(client):
    user = UserFactory.create(role=User.Role.CLIENT, first_login_completed=False)
    client.force_login(user)
    url = reverse("users:change_password")

    response = client.post(
        url,
        {
            "old_password": settings.TEST_USER_PASSWORD,
            "new_password1": "aioxRt6vc",
            "new_password2": "aioxRt6vc",
        },
    )

    assert response.status_code == http.HTTPStatus.FOUND
    assert response.url == reverse("users:index")
    user.refresh_from_db()
    assert user.first_login_completed is True


@pytest.mark.django_db
def test_profile_page_view_base_template_for_client(client):
    user = ClientFactory.create().user
    client.force_login(user)
    response = client.get(reverse("users:profile"))
    assert response.status_code == 200
    assert response.context["base_template"] == "base_client_role.html"


@pytest.mark.django_db
def test_profile_page_view_base_template_for_counselor(client):
    user = UserFactory.create(role=User.Role.COUNSELOR)
    client.force_login(user)
    response = client.get(reverse("users:profile"))
    assert response.status_code == 200
    assert response.context["base_template"] == "base_counselor_role.html"


@pytest.mark.django_db
def test_email_update_view_base_template_for_client(client):
    user = UserFactory.create(role=User.Role.CLIENT)
    client.force_login(user)
    response = client.get(reverse("users:change_email", kwargs={"pk": user.id}))
    assert response.status_code == 200
    assert response.context["base_template"] == "base_client_role.html"


@pytest.mark.django_db
def test_email_update_view_base_template_for_counselor(client):
    user = UserFactory.create(role=User.Role.COUNSELOR)
    client.force_login(user)
    response = client.get(reverse("users:change_email", kwargs={"pk": user.id}))
    assert response.status_code == 200
    assert response.context["base_template"] == "base_counselor_role.html"


@pytest.mark.django_db
def test_email_update_view(client):
    user = UserFactory.create(email="old_email@example.com")
    client.force_login(user)
    response = client.post(
        reverse("users:change_email", kwargs={"pk": user.id}),
        {"email": "new_email@example.com"},
    )
    assert response.status_code == 302
    assert response.url == reverse("users:index")
    user.refresh_from_db()
    assert user.email is None
    assert user.email_hash == hash_email("new_email@example.com")


@pytest.mark.django_db
def test_toggle_push_notifications_view(client):
    client_user = ClientFactory.create(push_notifications_granted=False)
    client.force_login(client_user.user)
    response = client.post(reverse("users:toggle_push_notifications"))
    assert response.status_code == 302
    assert response.url == reverse("users:profile")
    client_user.refresh_from_db()
    assert client_user.push_notifications_granted is True
    response = client.post(reverse("users:toggle_push_notifications"))
    assert response.status_code == 302
    assert response.url == reverse("users:profile")
    client_user.refresh_from_db()
    assert client_user.push_notifications_granted is False
