import pytest
from clients.tests.factories import ClientFactory
from diaries.tests.factories import MoodDiaryEntryFactory


@pytest.fixture
def create_response(client):
    def _create_response(user, url, method="GET", data=None, content_type=None):
        client.force_login(user)
        if not content_type:
            response = getattr(client, method.lower())(url, data)
        else:
            response = getattr(client, method.lower())(url, data, content_type=content_type)
        return response

    return _create_response


@pytest.fixture
def user():
    client = ClientFactory.create(push_notifications_granted=None)
    return client.user


@pytest.fixture
def entry(user):
    return MoodDiaryEntryFactory.create(mood_diary__client=user.client, released=False)
