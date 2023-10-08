import pytest
from django.conf import settings
from django.core import mail
from django.urls import reverse
from users.tests.factories import UserFactory


@pytest.mark.django_db
def test_counselor_creation_sends_email(admin_client, django_user_model):
    url = reverse("admin:users_user_add")
    data = {
        "email": "test@example.com",
        "role": f"{django_user_model.Role.COUNSELOR}",
        "is_staff": True,
        "_save": "Save",
    }
    response = admin_client.post(url, data)

    assert response.status_code == 302  # Redirect after creation
    assert django_user_model.objects.get(email="test@example.com") is not None
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to[0] == "test@example.com"
    assert mail.outbox[0].from_email == settings.FROM_EMAIL


@pytest.mark.django_db
def test_client_creation_does_not_send_email(admin_client, django_user_model):
    url = reverse("admin:users_user_add")
    data = {
        "email": "test@example.com",
        "role": f"{django_user_model.Role.CLIENT}",
        "is_staff": True,
        "_save": "Save",
    }
    response = admin_client.post(url, data)

    assert response.status_code == 302  # Redirect after creation
    assert django_user_model.objects.get(email="test@example.com") is not None
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_user_update_does_not_send_email(admin_client):
    user = UserFactory.create(email="test@example.com")
    url = reverse("admin:users_user_change", args=[user.pk])
    data = {"email": "another@example.com", "_save": "Save"}
    response = admin_client.post(url, data)

    # Check if the user was updated
    assert response.status_code == 302  # Redirect after update
    user.refresh_from_db()
    assert user.email == "another@example.com"
    assert len(mail.outbox) == 0
