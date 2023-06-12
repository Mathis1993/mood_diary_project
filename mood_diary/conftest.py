import pytest


@pytest.fixture
def create_response(client):
    def _create_response(user, url, method="GET", data=None):
        client.force_login(user)
        response = getattr(client, method.lower())(url, data)
        return response

    return _create_response
