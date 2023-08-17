import pytest
from clients.tests.factories import ClientFactory
from diaries.tests.factories import MoodDiaryEntryFactory


@pytest.fixture
def create_response(client):
    def _create_response(user, url, method="GET", data=None, content_type="application/json"):
        client.force_login(user)
        response = getattr(client, method.lower())(url, data, content_type=content_type)
        return response

    return _create_response


@pytest.fixture
def user():
    client = ClientFactory.create()
    return client.user


@pytest.fixture
def entry(user):
    return MoodDiaryEntryFactory.create(mood_diary__client=user.client, released=False)
