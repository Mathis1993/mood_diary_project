from core.views import AuthenticatedClientRoleMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from el_pagination.views import AjaxListView
from rules.models import RuleClient


class RuleListView(AuthenticatedClientRoleMixin, AjaxListView):
    model = RuleClient
    template_name = "rules/rules_list.html"
    page_template = "rules/rule_list_page.html"
    context_object_name = "rules"

    def get_queryset(self):
        return self.model.objects.filter(client_id=self.request.user.client.id).all()


class RuleClientUpdateToInactiveView(AuthenticatedClientRoleMixin, View):
    def post(self, request, pk):
        rule_client_obj = RuleClient.objects.get(id=pk)
        client_id = self.request.user.client.id
        if rule_client_obj.client_id == client_id:
            rule_client_obj.active = False
            rule_client_obj.save()
        return redirect(reverse_lazy("rules:get_all_rules"))


class RuleClientUpdateToActiveView(AuthenticatedClientRoleMixin, View):
    def post(self, request, pk):
        rule_client_obj = RuleClient.objects.get(id=pk)
        client_id = self.request.user.client.id
        if rule_client_obj.client_id == client_id:
            rule_client_obj.active = True
            rule_client_obj.save()
        return redirect(reverse_lazy("rules:get_all_rules"))
