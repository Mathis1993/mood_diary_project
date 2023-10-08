import pytest
from core.utils import hash_email, send_account_creation_email
from django.conf import settings
from django.core import mail
from django.core.exceptions import ValidationError
from pytest_mock import MockFixture


def test_send_account_creation_email():
    send_account_creation_email("a@b.de", "localhost", "http", "password")
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to[0] == "a@b.de"
    assert mail.outbox[0].from_email == settings.FROM_EMAIL


def test_send_account_creation_email_fails(mocker: MockFixture):
    mocker.patch("core.utils.send_mail", side_effect=Exception)
    with pytest.raises(ValidationError):
        send_account_creation_email("a@b.de", "localhost", "http", "password")
    assert len(mail.outbox) == 0


def test_hash_email():
    email = "myemailaddress@mydomain.de"
    hashed_email_1 = hash_email(email)
    hashed_email_2 = hash_email(email)
    # Ensure the function is well-defined
    assert hashed_email_1 == hashed_email_2
    assert hashed_email_1 != email
    assert len(hashed_email_1) == 64
