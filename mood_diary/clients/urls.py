"""
URL patterns for the clients app.
"""

from clients import views
from django.urls import path

app_name = "clients"

urlpatterns = [
    path("create/", views.CreateClientView.as_view(), name="create_client"),
    path("get_all/", views.ClientListView.as_view(), name="list_clients"),
    path(
        "<int:pk>/update_to_inactive/",
        views.ClientUpdateToInactiveView.as_view(),
        name="update_to_inactive",
    ),
    path(
        "<int:client_pk>/mood_diary_entries/<int:entry_pk>/get/",
        views.MoodDiaryEntryDetailView.as_view(),
        name="get_mood_diary_entry_client",
    ),
    path(
        "<int:client_pk>/mood_diary_entries/get_all/",
        views.MoodDiaryEntryListCounselorView.as_view(),
        name="list_mood_diary_entries_client",
    ),
]
