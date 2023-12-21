import pytest
from django.conf import settings
from django.test import RequestFactory
from users.authentication_backends import EmailHashBackend
from users.tests.factories import UserFactory


@pytest.mark.django_db
def test_email_hash_backend():
    user_active = UserFactory.create(email="a@b.de", is_active=True)
    UserFactory.create(email="c@d.de", is_active=False)
    factory = RequestFactory()
    request = factory.get("/some-path/")
    backend = EmailHashBackend()

    # active user, email in kwarg
    user = backend.authenticate(
        request, username=None, password=settings.TEST_USER_PASSWORD, email="a@b.de"
    )
    assert user == user_active

    # active user, email in username
    user = backend.authenticate(request, username="a@b.de", password=settings.TEST_USER_PASSWORD)
    assert user == user_active

    # inactive user
    user = backend.authenticate(request, username="c@d.de", password=settings.TEST_USER_PASSWORD)
    assert user is None

    # wrong password
    user = backend.authenticate(
        request, username="a@b.de", password=settings.TEST_USER_PASSWORD + "wrong"
    )
    assert user is None

    # no email anywhere
    user = backend.authenticate(
        request, username=None, password=settings.TEST_USER_PASSWORD, email=None
    )
    assert user is None

    # no password
    user = backend.authenticate(request, username="a@b.de", password=None)
    assert user is None

    # non-existing user
    user = backend.authenticate(request, username="e@f.de", password="password2")
    assert user is None
