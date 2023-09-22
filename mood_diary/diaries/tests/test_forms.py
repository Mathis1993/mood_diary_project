import pytest
from diaries.forms import ActivityWidget, MoodDiaryEntryCreateForm, MoodDiaryEntryForm
from diaries.tests.factories import ActivityFactory, MoodFactory
from django.urls import reverse


@pytest.fixture
def valid_mood_diary_entry_form_data():
    mood = MoodFactory.create(value=0)
    activity = ActivityFactory.create()
    return {
        "date": "2023-10-12",
        "start_time": "09:00",
        "end_time": "10:00",
        "activity": activity.id,
        "mood": mood.id,
        "details": "Feeling good",
    }


@pytest.fixture
def valid_mood_diary_entry_create_form_data(valid_mood_diary_entry_form_data):
    valid_mood_diary_entry_form_data["end_date"] = "2023-10-13"
    return valid_mood_diary_entry_form_data


@pytest.mark.django_db
def test_valid_mood_diary_entry_form(valid_mood_diary_entry_form_data):
    form = MoodDiaryEntryForm(data=valid_mood_diary_entry_form_data)
    valid = form.is_valid()
    assert valid


@pytest.mark.django_db
def test_mood_diary_entry_form_required_fields():
    MoodFactory.create(value=0)
    form = MoodDiaryEntryForm(data={})
    assert not form.is_valid()
    assert "date" in form.errors
    assert "mood" in form.errors
    assert "activity" in form.errors


@pytest.mark.django_db
def test_mood_diary_entry_create_form_clean(valid_mood_diary_entry_form_data):
    # start_date and end_date filled (valid)
    form = MoodDiaryEntryCreateForm(data=valid_mood_diary_entry_form_data)
    assert form.is_valid()

    # start_date and end_date filled (invalid)
    valid_mood_diary_entry_form_data["end_date"] = "2023-10-11"
    form = MoodDiaryEntryCreateForm(data=valid_mood_diary_entry_form_data)
    assert not form.is_valid()

    # end_date not filled
    valid_mood_diary_entry_form_data.pop("end_date")
    form = MoodDiaryEntryCreateForm(data=valid_mood_diary_entry_form_data)
    assert form.is_valid()
    assert form.cleaned_data["end_date"] == form.cleaned_data["date"]


# Right now excluded from form
# @pytest.mark.django_db
# def test_dependent_strain_fields(valid_mood_diary_entry_form_data):
#     strain_area = StrainAreaFactory.create()
#
#     # Set strain area without strain
#     valid_form_data["strain"] = None
#     valid_form_data["strain_area"] = strain_area.id
#     form = MoodDiaryEntryForm(data=valid_form_data)
#     assert not form.is_valid()
#     assert "strain_area" in form.errors
#
#     # Set strain info without strain
#     valid_form_data["strain_info"] = "Some info"
#     form = MoodDiaryEntryForm(data=valid_form_data)
#     assert not form.is_valid()
#     assert "strain_info" in form.errors


def test_activity_widget_search_fields():
    widget = ActivityWidget()
    expected_search_fields = [
        "value_de__icontains",
        "value_en__icontains",
        "category__value_de__icontains",
        "category__value_en__icontains",
    ]
    assert widget.search_fields == expected_search_fields


def test_activity_widget_data_url():
    widget = ActivityWidget()
    expected_url = reverse("diaries:mood_diary_entries_create_auto_select")
    assert widget.data_url == expected_url


def test_activity_widget_attrs():
    widget = ActivityWidget()
    assert widget.attrs["data-minimum-input-length"] == 0
