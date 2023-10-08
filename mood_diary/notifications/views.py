import http
import json

from core.views import AuthenticatedClientRoleMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.views import View
from django.views.generic import DetailView
from el_pagination.views import AjaxListView
from notifications.models import Notification


class RestrictNotificationToOwnerMixin:
    """
    Mixin to restrict access to a notification to its owner.
    """

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(client_id=self.request.user.client.id).all()


class NotificationListView(
    AuthenticatedClientRoleMixin, RestrictNotificationToOwnerMixin, AjaxListView
):
    """
    View for displaying a list of notifications.
    """

    model = Notification
    template_name = "notifications/notifications_list.html"
    page_template = "notifications/notification_list_page.html"
    context_object_name = "notifications"


class NotificationDetailView(
    AuthenticatedClientRoleMixin, RestrictNotificationToOwnerMixin, DetailView
):
    """
    View for displaying a notification in detail.
    """

    model = Notification
    template_name = "notifications/notification_get.html"
    context_object_name = "notification"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Upon receiving a GET request, display the requested notification
        and set its viewed attribute to True.

        Parameters
        ----------
        request: HttpRequest
        args: list
        kwargs: dict

        Returns
        -------
        HttpResponse
        """
        notification = self.get_object()
        notification.viewed = True
        notification.save()
        return super().get(request, *args, **kwargs)


class UpdateNotificationsPermissionView(AuthenticatedClientRoleMixin, View):
    """
    View for updating the notifications permission of a client.
    """

    template_name = "dashboards/dashboard_client.html"

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Upon receiving a POST request, update the notifications permission of the client
        by setting the boolean field `push_notifications_granted`.

        Parameters
        ----------
        request: HttpRequest

        Returns
        -------
        HttpResponse
        """
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
    """
    View for creating a push subscription for a client.
    Only creates a subscription if the provided subscription does not exist yet
    for this client.
    """

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Upon receiving a POST request, create a push subscription for the client
        (if it does not exist already).

        Parameters
        ----------
        request: HttpRequest

        Returns
        -------
        HttpResponse
        """
        subscription = json.loads(request.body)
        client = request.user.client
        _, created = client.push_subscriptions.get_or_create(
            subscription__endpoint=subscription["endpoint"], defaults={"subscription": subscription}
        )
        if created:
            return HttpResponse(status=http.HTTPStatus.CREATED)
        return HttpResponse(status=http.HTTPStatus.OK)
