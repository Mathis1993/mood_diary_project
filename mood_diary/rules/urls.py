"""
URL patterns for the notifications app.
"""

from django.urls import path
from rules import views

app_name = "rules"

urlpatterns = [
    path(
        "rules/get_all/",
        views.RuleListView.as_view(),
        name="get_all_rules",
    ),
    path(
        "<int:pk>/update_to_inactive/",
        views.RuleClientUpdateToInactiveView.as_view(),
        name="update_to_inactive",
    ),
    path(
        "<int:pk>/update_to_active/",
        views.RuleClientUpdateToActiveView.as_view(),
        name="update_to_active",
    ),
]
