import pytest
from users.forms import UserEmailForm


@pytest.mark.django_db
def test_valid_email():
    form = UserEmailForm(data={"email": "test@example.com"})
    assert form.is_valid()


@pytest.mark.django_db
def test_invalid_email():
    form = UserEmailForm(data={"email": "invalid-email"})
    assert not form.is_valid()
    assert "email" in form.errors


def test_widget_class():
    form = UserEmailForm()
    assert "form-control" in form.fields["email"].widget.attrs["class"]
