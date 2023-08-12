from core.utils import send_account_creation_email
from django.conf import settings
from django.core import mail
from pytest_mock import MockFixture


def test_send_account_creation_email():
    send_account_creation_email("a@b.de", "localhost", "http", "password")
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to[0] == "a@b.de"
    assert mail.outbox[0].from_email == settings.FROM_EMAIL


def test_send_account_creation_email_fails(mocker: MockFixture):
    mocker.patch("core.utils.send_mail", side_effect=Exception)
    send_account_creation_email("a@b.de", "localhost", "http", "password")
    assert len(mail.outbox) == 0
