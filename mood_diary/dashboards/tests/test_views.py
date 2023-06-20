import http
from datetime import datetime
from unittest import mock

import pytest
from clients.tests.factories import ClientFactory
from diaries.models import Activity, Mood, MoodDiary, MoodDiaryEntry
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.tests.factories import UserFactory

User = get_user_model()


@pytest.fixture
def user():
    client = ClientFactory.create()
    return client.user


@pytest.fixture
def mood_diary(user):
    return MoodDiary.objects.create(client=user.client)


@pytest.fixture
def mood_scores(mood_diary):
    class MockQuerySet:
        data = [
            {"date": datetime(2023, 10, 1).date(), "average_mood": 8},
            {"date": datetime(2023, 10, 2).date(), "average_mood": 9},
            {"date": datetime(2023, 10, 3).date(), "average_mood": 10},
        ]

        def values_list(self, *args, **kwargs):
            if args[0] == "date":
                return [item["date"] for item in self.data]
            if args[0] == "average_mood":
                return [item["average_mood"] for item in self.data]

    return MockQuerySet()


@pytest.fixture
def mood_highlights(mood_diary):
    return [
        MoodDiaryEntry(
            date="2023-06-07", mood=Mood(value=7, label="Happiest"), activity=Activity(value="A1")
        ),
        MoodDiaryEntry(
            date="2023-06-06", mood=Mood(value=6, label="Happier"), activity=Activity(value="A2")
        ),
        MoodDiaryEntry(
            date="2023-06-05", mood=Mood(value=5, label="Happy"), activity=Activity(value="A3")
        ),
    ]


@pytest.mark.django_db
@mock.patch("diaries.models.MoodDiary.average_mood_scores_previous_days")
@mock.patch("diaries.models.MoodDiary.most_recent_mood_highlights")
def test_dashboard_client_view(
    mock_highlights, mock_scores, user, mood_diary, mood_scores, mood_highlights, create_response
):
    url = reverse("dashboards:dashboard_client")
    mock_scores.return_value = mood_scores
    mock_highlights.return_value = mood_highlights

    response = create_response(user, url)

    assert response.status_code == http.HTTPStatus.OK
    assert response.context["mood_scores_dates"] == ["Sunday", "Monday", "Tuesday"]
    assert response.context["mood_scores_values"] == [8, 9, 10]
    assert response.context["mood_highlights"] == mock_highlights.return_value


@pytest.mark.django_db
def test_dashboard_counselor_view(create_response):
    counselor = UserFactory.create(role=User.Role.COUNSELOR)
    url = reverse("dashboards:dashboard_counselor")

    response = create_response(counselor, url)

    assert response.status_code == http.HTTPStatus.OK
