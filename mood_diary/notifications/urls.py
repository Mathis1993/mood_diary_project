from django.urls import path
from notifications import views

app_name = "notifications"

urlpatterns = [
    path(
        "notifications/<int:pk>/get/",
        views.NotificationDetailView.as_view(),
        name="get_notification",
    ),
    path(
        "notifications/get_all/",
        views.NotificationListView.as_view(),
        name="get_all_notifications",
    ),
    path(
        "push_subscriptions/create/",
        views.PushSubscriptionCreateView.as_view(),
        name="create_push_subscription",
    ),
]
