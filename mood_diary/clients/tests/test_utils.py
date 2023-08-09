from clients.utils import send_account_creation_email
from django.conf import settings
from django.core import mail


def test_send_account_creation_email():
    send_account_creation_email("a@b.de", "localhost", "http", "password")
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to[0] == "a@b.de"
    assert mail.outbox[0].from_email == settings.FROM_EMAIL
