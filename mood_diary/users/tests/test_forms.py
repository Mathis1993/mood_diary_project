import pytest
from users.forms import CustomPasswordResetForm, CustomSetPasswordForm
from users.tests.factories import UserFactory

# Because the email address is used to encrypt the mood diary entry detail field,
# we disable the possibility to change the email address for now.
# @pytest.mark.django_db
# def test_valid_email():
#     form = UserEmailForm(data={"email": "test@example.com"})
#     assert form.is_valid()
#
#
# @pytest.mark.django_db
# def test_invalid_email():
#     form = UserEmailForm(data={"email": "invalid-email"})
#     assert not form.is_valid()
#     assert "email" in form.errors


@pytest.mark.django_db
def test_widget_class():
    user = UserFactory.create()
    form = CustomSetPasswordForm(user)
    assert "form-control" in form.fields["new_password1"].widget.attrs["class"]
    assert "form-control" in form.fields["new_password2"].widget.attrs["class"]


@pytest.mark.django_db
def test_password_reset_form_get_users():
    user = UserFactory.create(email="a@b.de")
    form = CustomPasswordResetForm()
    users = form.get_users("c@d.de")
    assert sum(1 for _ in users) == 0
    users = form.get_users("a@b.de")
    users = [u for u in users]
    assert len(users) == 1
    assert users[0] == user
    assert users[0].email == "a@b.de"
    user.refresh_from_db()
    assert user.email is None
