import datetime
import http
from datetime import date
from unittest.mock import patch

import pytest
from clients.tests.factories import ClientFactory
from diaries.forms import ActivityWidget, MoodDiaryEntryForm
from diaries.models import Activity, MoodDiaryEntry
from diaries.tests.factories import (
    ActivityCategoryFactory,
    ActivityFactory,
    MoodDiaryEntryFactory,
    MoodDiaryFactory,
    MoodFactory,
)
from diaries.views import ActivitySelect2QuerySetView
from django.urls import reverse
from django.utils import timezone
from pytest_mock import MockerFixture


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
    other_client = ClientFactory.create()
    MoodDiaryEntryFactory.create(mood_diary__client=other_client)
    assert MoodDiaryEntry.objects.count() == 2
    url = reverse("diaries:list_mood_diary_entries")

    response = create_response(user, url)

    assert response.status_code == http.HTTPStatus.OK
    assert entry in (response_entries := response.context_data["entries"])
    assert response_entries.count() == 1
    assert "diaries/mood_diary_entries_list.html" in response.template_name


@pytest.mark.django_db
def test_mood_diary_entry_create_view_get(user, create_response):
    MoodFactory.create(value=0)
    url = reverse("diaries:create_mood_diary_entry")

    response = create_response(user, url)

    assert response.status_code == http.HTTPStatus.OK
    assert isinstance(response.context["form"], MoodDiaryEntryForm)


@pytest.mark.django_db
def test_mood_diary_entry_create_view_post(user, create_response, mocker: MockerFixture):
    mocked_task = mocker.patch("diaries.views.task_event_based_rules_evaluation.delay")
    MoodDiaryFactory.create(client=user.client)
    mood = MoodFactory.create(value=0)
    activity = ActivityFactory.create()
    url = reverse("diaries:create_mood_diary_entry")

    assert not MoodDiaryEntry.objects.exists()

    response = create_response(
        user,
        url,
        method="POST",
        data={
            "date": date.today(),
            "start_time": "12:00",
            "end_time": "13:00",
            "mood": mood.id,
            "activity": activity.id,
        },
    )

    assert response.status_code == http.HTTPStatus.FOUND
    assert response.url == reverse("diaries:list_mood_diary_entries")
    assert MoodDiaryEntry.objects.count() == 1
    assert mocked_task.call_count == 1
    assert mocked_task.call_args_list[0][0][0].client_id == user.client.id


@pytest.mark.django_db
def test_mood_diary_entry_create_view_post_multiple_days(
    user, create_response, mocker: MockerFixture
):
    mocked_task = mocker.patch("diaries.views.task_event_based_rules_evaluation.delay")
    MoodDiaryFactory.create(client=user.client)
    mood = MoodFactory.create(value=0)
    activity = ActivityFactory.create()
    url = reverse("diaries:create_mood_diary_entry")

    assert not MoodDiaryEntry.objects.exists()

    response = create_response(
        user,
        url,
        method="POST",
        data={
            "date": date.today(),
            "end_date": date.today() + timezone.timedelta(days=2),
            "start_time": "12:00",
            "end_time": "13:00",
            "mood": mood.id,
            "activity": activity.id,
        },
    )

    assert response.status_code == http.HTTPStatus.FOUND
    assert response.url == reverse("diaries:list_mood_diary_entries")
    assert MoodDiaryEntry.objects.count() == 3
    entries = MoodDiaryEntry.objects.all().order_by("date")
    assert entries[0].date == date.today()
    assert entries[0].start_time == datetime.time(12, 0, 0)
    assert entries[0].end_time == datetime.time(23, 59, 59)
    assert entries[1].date == date.today() + timezone.timedelta(days=1)
    assert entries[1].start_time == datetime.time(0, 0, 0)
    assert entries[1].end_time == datetime.time(23, 59, 59)
    assert entries[2].date == date.today() + timezone.timedelta(days=2)
    assert entries[2].start_time == datetime.time(0, 0, 0)
    assert entries[2].end_time == datetime.time(13, 0, 0)
    assert mocked_task.call_count == 3
    assert mocked_task.call_args_list[0][0][0].client_id == user.client.id
    assert mocked_task.call_args_list[1][0][0].client_id == user.client.id
    assert mocked_task.call_args_list[2][0][0].client_id == user.client.id


@pytest.mark.django_db
def test_mood_diary_entry_update_view_get(user, entry, create_response):
    MoodFactory.create(value=0)
    url = reverse("diaries:update_mood_diary_entry", kwargs={"pk": entry.pk})

    response = create_response(user, url)

    assert response.status_code == http.HTTPStatus.OK
    assert isinstance(response.context_data["view"].object, MoodDiaryEntry)
    assert "diaries/mood_diary_entry_update.html" in response.template_name


@pytest.mark.django_db
def test_mood_diary_entry_update_view_post(user, entry, create_response, mocker: MockerFixture):
    mocked_task = mocker.patch("diaries.views.task_event_based_rules_evaluation.delay")
    MoodFactory.create(value=0)
    url = reverse("diaries:update_mood_diary_entry", kwargs={"pk": entry.pk})

    response = create_response(
        user,
        url,
        method="POST",
        data={
            "date": date.today(),
            "start_time": "12:00",
            "end_time": "13:00",
            "mood": entry.mood_id,
            "activity": entry.activity_id,
        },
    )

    assert response.status_code == http.HTTPStatus.FOUND
    assert response.url == reverse("diaries:get_mood_diary_entry", kwargs={"pk": entry.pk})
    entry.refresh_from_db()
    assert entry.start_time.strftime("%H:%M") == "12:00"
    assert entry.end_time.strftime("%H:%M") == "13:00"
    assert mocked_task.call_count == 1
    assert mocked_task.call_args_list[0][0][0].client_id == user.client.id


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


@pytest.mark.django_db
def test_mood_diary_entry_release_view_post(user, entry, create_response):
    MoodDiaryEntryFactory.create_batch(size=3, mood_diary__client=user.client, released=False)

    url = reverse("diaries:release_mood_diary_entries")

    assert MoodDiaryEntry.objects.filter(released=True).count() == 0

    response = create_response(user, url, method="POST")

    assert response.status_code == 302
    assert response.url == reverse("diaries:list_mood_diary_entries")
    assert not MoodDiaryEntry.objects.filter(released=True).count() == 3


@pytest.mark.django_db
def test_activity_select2_queryset_view_grouped_response(client):
    category1 = ActivityCategoryFactory.create(
        value="Category_1",
        value_de="Kategorie_1",
        value_en="Category_1",
    )
    category2 = ActivityCategoryFactory.create(
        value="Category_2",
        value_de="Kategorie_2",
        value_en="Category_2",
    )
    ActivityFactory.create(
        category=category1,
        value="Activity_1",
        value_de="Aktivität_1",
        value_en="Activity_1",
    )
    ActivityFactory.create(
        category=category1,
        value="Activity_2",
        value_de="Aktivität_2",
        value_en="Activity_2",
    )
    ActivityFactory.create(
        category=category2,
        value="Activity_3",
        value_de="Aktivität_3",
        value_en="Activity_3",
    )

    with patch.object(
        ActivitySelect2QuerySetView,
        "get_widget_or_404",
        return_value=ActivityWidget(queryset=Activity.objects.all()),
    ):
        response = client.get(
            reverse("diaries:mood_diary_entries_create_auto_select"),
            HTTP_ACCEPT="application/json",
            HTTP_ACCEPT_LANGUAGE="de",
        )
    data = response.json()

    assert len(data["results"]) == 2
    assert data["results"][0]["text"] == "Kategorie_1"
    assert len(children := data["results"][0]["children"]) == 2
    assert children[0]["text"] == "Aktivität_1"


@pytest.mark.django_db
def test_activity_select2_queryset_view_ordering_by_language(client):
    category = ActivityCategoryFactory(value="Category", value_de="Kategorie", value_en="Category")
    ActivityFactory(category=category, value="Activity", value_de="Aktivität", value_en="Activity")

    with patch.object(
        ActivitySelect2QuerySetView,
        "get_widget_or_404",
        return_value=ActivityWidget(queryset=Activity.objects.all()),
    ):
        response = client.get(
            reverse("diaries:mood_diary_entries_create_auto_select"),
            HTTP_ACCEPT_LANGUAGE="en",
        )
    data = response.json()

    assert data["results"][0]["text"] == "Category"
    assert data["results"][0]["children"][0]["text"] == "Activity"
