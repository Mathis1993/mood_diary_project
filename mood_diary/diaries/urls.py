"""
URL patterns for the diaries app.
"""

from diaries import views
from django.urls import path

app_name = "diaries"

urlpatterns = [
    path(
        "mood_diary_entries/<int:pk>/get/",
        views.MoodDiaryEntryDetailView.as_view(),
        name="get_mood_diary_entry",
    ),
    path(
        "mood_diary_entries/get_all/",
        views.MoodDiaryEntryListView.as_view(),
        name="list_mood_diary_entries",
    ),
    path(
        "mood_diary_entries/create/",
        views.MoodDiaryEntryCreateView.as_view(),
        name="create_mood_diary_entry",
    ),
    path(
        "mood_diary_entries/<int:pk>/update/",
        views.MoodDiaryEntryUpdateView.as_view(),
        name="update_mood_diary_entry",
    ),
    path(
        "mood_diary_entries/<int:pk>/delete/",
        views.MoodDiaryEntryDeleteView.as_view(),
        name="delete_mood_diary_entry",
    ),
    path(
        "mood_diary_entries/release/",
        views.MoodDiaryEntryReleaseView.as_view(),
        name="release_mood_diary_entries",
    ),
    path(
        "mood_diary_entries/auto_select/auto.json",
        views.ActivitySelect2QuerySetView.as_view(),
        name="mood_diary_entries_create_auto_select",
    ),
]
