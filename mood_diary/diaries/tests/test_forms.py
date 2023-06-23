import pytest
from diaries.forms import MoodDiaryEntryForm
from diaries.tests.factories import ActivityFactory, MoodFactory


@pytest.fixture
def valid_form_data():
    mood = MoodFactory.create(value=0)
    activity = ActivityFactory.create()
    return {
        "date": "2023-10-12",
        "start_time": "09:00",
        "end_time": "10:00",
        "activity": activity.id,
        "mood": mood.id,
        "mood_and_emotion_info": "Feeling good",
    }


@pytest.mark.django_db
def test_valid_form(valid_form_data):
    form = MoodDiaryEntryForm(data=valid_form_data)
    valid = form.is_valid()
    assert valid


@pytest.mark.django_db
def test_required_fields():
    MoodFactory.create(value=0)
    form = MoodDiaryEntryForm(data={})
    assert not form.is_valid()
    assert "date" in form.errors
    assert "mood" in form.errors
    assert "activity" in form.errors


# Right now excluded from form
# @pytest.mark.django_db
# def test_dependent_strain_fields(valid_form_data):
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
