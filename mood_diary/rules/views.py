from core.views import AuthenticatedClientRoleMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from el_pagination.views import AjaxListView
from rules.models import RuleClient


class RuleListView(AuthenticatedClientRoleMixin, AjaxListView):
    """
    View for displaying a list of rules.
    """

    model = RuleClient
    template_name = "rules/rules_list.html"
    page_template = "rules/rule_list_page.html"
    context_object_name = "rules"

    def get_queryset(self) -> QuerySet[RuleClient]:
        """
        Return a queryset of RuleClient objects for the requesting client.

        Returns
        -------
        QuerySet[RuleClient]
        """
        return self.model.objects.filter(client_id=self.request.user.client.id).all()


class RuleClientUpdateToInactiveView(AuthenticatedClientRoleMixin, View):
    """
    View for updating a rule to inactive.
    """

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """
        Upon receiving a POST request, update the requested rule to be inactive
        for the requesting client.
        Only do so if the RuleClient entity indicated by the pk argument belongs
        to the requesting client.

        Parameters
        ----------
        request: HttpRequest
        pk: int
            RuleClient entity id

        Returns
        -------
        HttpResponse
            Redirect to the rule list view.
        """
        rule_client_obj = RuleClient.objects.get(id=pk)
        client_id = self.request.user.client.id
        if rule_client_obj.client_id == client_id:
            rule_client_obj.active = False
            rule_client_obj.save()
        return redirect(reverse_lazy("rules:get_all_rules"))


class RuleClientUpdateToActiveView(AuthenticatedClientRoleMixin, View):
    """
    View for updating a rule to active.
    """

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """
        Upon receiving a POST request, update the requested rule to be active
        for the requesting client.
        Only do so if the RuleClient entity indicated by the pk argument belongs
        to the requesting client.

        Parameters
        ----------
        request: HttpRequest
        pk: int
            RuleClient entity id

        Returns
        -------
        HttpResponse
            Redirect to the rule list view.
        """
        rule_client_obj = RuleClient.objects.get(id=pk)
        client_id = self.request.user.client.id
        if rule_client_obj.client_id == client_id:
            rule_client_obj.active = True
            rule_client_obj.save()
        return redirect(reverse_lazy("rules:get_all_rules"))
