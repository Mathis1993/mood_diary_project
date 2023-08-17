from dashboards import views
from django.urls import path

app_name = "dashboards"

urlpatterns = [
    path(
        "client/",
        views.DashboardClientView.as_view(),
        name="dashboard_client",
    ),
    path(
        "client/update_notifications_permission/",
        views.UpdateNotificationsPermissionView.as_view(),
        name="update_notifications_permission",
    ),
]
