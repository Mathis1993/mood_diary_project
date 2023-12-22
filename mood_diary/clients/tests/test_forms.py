from clients.forms import ClientCreationForm


def test_client_creation_form_valid_data():
    form = ClientCreationForm(
        data={"email": "test@example.com", "identifier": "client1", "client_key_encrypted": "key"}
    )

    assert form.is_valid()


def test_client_creation_form_missing_data():
    form = ClientCreationForm(data={"email": "test@example.com", "client_key_encrypted": "key"})

    assert not form.is_valid()
    assert "identifier" in form.errors


def test_client_creation_form_invalid_data():
    form = ClientCreationForm(
        data={"email": "invalid-email", "identifier": "client1", "client_key_encrypted": "key"}
    )

    assert not form.is_valid()
    assert "email" in form.errors
