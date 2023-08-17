import http
import json

from core.views import AuthenticatedClientRoleMixin
from django.http import HttpResponse
from django.views import View
from django.views.generic import DetailView
from el_pagination.views import AjaxListView
from notifications.models import Notification


class RestrictNotificationToOwnerMixin:
    def get_queryset(self):
        return self.model.objects.filter(client_id=self.request.user.client.id).all()


class NotificationListView(
    AuthenticatedClientRoleMixin, RestrictNotificationToOwnerMixin, AjaxListView
):
    model = Notification
    template_name = "notifications/notifications_list.html"
    page_template = "notifications/notification_list_page.html"
    context_object_name = "notifications"


class NotificationDetailView(
    AuthenticatedClientRoleMixin, RestrictNotificationToOwnerMixin, DetailView
):
    model = Notification
    template_name = "notifications/notification_get.html"
    context_object_name = "notification"

    def get(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.viewed = True
        notification.save()
        return super().get(request, *args, **kwargs)


# ToDo(ME-16.08.23): Test
# ToDo(ME-16.08.23): Way to enable/disable push notifications
#  (add "notifications" entry to settings dropdown?)
class UpdateNotificationsPermissionView(AuthenticatedClientRoleMixin, View):
    template_name = "dashboards/dashboard_client.html"

    def post(self, request):
        data = json.loads(request.body)
        permission = data.get("permission")
        client = request.user.client
        if permission == "granted":
            client.push_notifications_granted = True
            client.save()
        else:
            client.push_notifications_granted = False
            client.save()
        return HttpResponse(status=http.HTTPStatus.OK)


class PushSubscriptionCreateView(AuthenticatedClientRoleMixin, View):
    def post(self, request):
        subscription = json.loads(request.body)
        client = request.user.client
        _, created = client.push_subscriptions.get_or_create(
            subscription__endpoint=subscription["endpoint"], defaults={"subscription": subscription}
        )
        if created:
            return HttpResponse(status=http.HTTPStatus.CREATED)
        return HttpResponse(status=http.HTTPStatus.OK)
