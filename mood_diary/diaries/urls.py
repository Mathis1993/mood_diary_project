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
        views.CreateMoodDiaryEntryView.as_view(),
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
]
