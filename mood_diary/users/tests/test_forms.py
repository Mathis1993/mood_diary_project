import pytest
from users.forms import CustomSetPasswordForm, UserEmailForm
from users.tests.factories import UserFactory


@pytest.mark.django_db
def test_valid_email():
    form = UserEmailForm(data={"email": "test@example.com"})
    assert form.is_valid()


@pytest.mark.django_db
def test_invalid_email():
    form = UserEmailForm(data={"email": "invalid-email"})
    assert not form.is_valid()
    assert "email" in form.errors


@pytest.mark.django_db
def test_widget_class():
    form = UserEmailForm()
    assert "form-control" in form.fields["email"].widget.attrs["class"]
    user = UserFactory.create()
    form = CustomSetPasswordForm(user)
    assert "form-control" in form.fields["new_password1"].widget.attrs["class"]
    assert "form-control" in form.fields["new_password2"].widget.attrs["class"]
