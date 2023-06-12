import http
from datetime import date

import pytest
from clients.tests.factories import ClientFactory
from diaries.forms import MoodDiaryEntryForm
from diaries.models import MoodDiaryEntry
from diaries.tests.factories import (
    ActivityFactory,
    MoodDiaryEntryFactory,
    MoodDiaryFactory,
    MoodFactory,
)
from django.urls import reverse


@pytest.fixture
def user():
    client = ClientFactory.create()
    return client.user


@pytest.fixture
def entry(user):
    return MoodDiaryEntryFactory.create(mood_diary__client=user.client)


@pytest.mark.django_db
def test_mood_diary_entry_detail_view(user, entry, create_response):
    url = reverse("diaries:get_mood_diary_entry", kwargs={"pk": entry.pk})
    response = create_response(user, url)

    assert response.status_code == http.HTTPStatus.OK
    assert response.context_data["entry"] == entry


@pytest.mark.django_db
def test_mood_diary_entry_detail_view_restricted(user, entry, create_response):
    other_client = ClientFactory.create()
    url = reverse("diaries:get_mood_diary_entry", kwargs={"pk": entry.pk})

    response = create_response(other_client.user, url)

    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_mood_diary_entry_list_view(user, entry, create_response):
    url = reverse("diaries:list_mood_diary_entries")

    response = create_response(user, url)

    assert response.status_code == http.HTTPStatus.OK
    assert entry in response.context_data["entries"]
    assert "diaries/mood_diary_entries_list.html" in response.template_name


@pytest.mark.django_db
def test_create_mood_diary_entry_view_get(user, create_response):
    url = reverse("diaries:create_mood_diary_entry")

    response = create_response(user, url)

    assert response.status_code == http.HTTPStatus.OK
    assert isinstance(response.context["form"], MoodDiaryEntryForm)


@pytest.mark.django_db
def test_create_mood_diary_entry_view_post(user, create_response):
    MoodDiaryFactory.create(client=user.client)
    mood = MoodFactory.create()
    activity = ActivityFactory.create()
    url = reverse("diaries:create_mood_diary_entry")

    assert not MoodDiaryEntry.objects.exists()

    response = create_response(
        user,
        url,
        method="POST",
        data={"date": date.today(), "mood": mood.id, "activity": activity.id},
    )

    assert response.status_code == http.HTTPStatus.FOUND
    assert response.url == reverse("diaries:list_mood_diary_entries")
    assert MoodDiaryEntry.objects.exists()


@pytest.mark.django_db
def test_mood_diary_entry_update_view_get(user, entry, create_response):
    url = reverse("diaries:update_mood_diary_entry", kwargs={"pk": entry.pk})

    response = create_response(user, url)

    assert response.status_code == http.HTTPStatus.OK
    assert isinstance(response.context_data["view"].object, MoodDiaryEntry)
    assert "diaries/mood_diary_entry_update.html" in response.template_name


@pytest.mark.django_db
def test_mood_diary_entry_update_view_post(user, entry, create_response):
    url = reverse("diaries:update_mood_diary_entry", kwargs={"pk": entry.pk})

    response = create_response(
        user,
        url,
        method="POST",
        data={
            "start_time": "12:00",
            "end_time": "13:00",
            "mood": entry.mood_id,
            "activity": entry.activity_id,
        },
    )

    assert response.status_code == http.HTTPStatus.FOUND
    assert response.url == reverse("diaries:list_mood_diary_entries")
    entry.refresh_from_db()
    assert entry.start_time.strftime("%H:%M") == "12:00"
    assert entry.end_time.strftime("%H:%M") == "13:00"


@pytest.mark.django_db
def test_mood_diary_entry_delete_view_get(user, entry, create_response):
    url = reverse("diaries:delete_mood_diary_entry", kwargs={"pk": entry.pk})

    response = create_response(user, url)

    assert response.status_code == 200
    assert isinstance(response.context_data["view"].object, MoodDiaryEntry)
    assert "diaries/mood_diary_entry_delete.html" in response.template_name


@pytest.mark.django_db
def test_mood_diary_entry_delete_view_post(user, entry, create_response):
    url = reverse("diaries:delete_mood_diary_entry", kwargs={"pk": entry.pk})

    assert MoodDiaryEntry.objects.exists()

    response = create_response(user, url, method="POST")

    assert response.status_code == 302
    assert response.url == reverse("diaries:list_mood_diary_entries")
    assert not MoodDiaryEntry.objects.exists()
