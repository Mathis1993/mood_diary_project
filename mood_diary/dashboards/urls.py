from dashboards import views
from django.urls import path

app_name = "dashboards"

urlpatterns = [
    path(
        "counselor/",
        views.DashboardCounselorView.as_view(),
        name="dashboard_counselor",
    ),
    path(
        "client/",
        views.DashboardClientView.as_view(),
        name="dashboard_client",
    ),
]
