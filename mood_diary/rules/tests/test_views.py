import http

import pytest
from clients.tests.factories import ClientFactory
from django.urls import reverse
from rules.models import Rule, RuleClient
from rules.tests.factories import RuleClientFactory, RuleFactory


@pytest.mark.django_db
def test_rules_list_view(user, create_response):
    rule_a = RuleFactory.create(title="A")
    rule_b = RuleFactory.create(title="B")

    assert Rule.objects.count() == 2
    url = reverse("rules:get_all_rules")

    # No rule subscribed by client
    response = create_response(user, url)
    assert response.status_code == http.HTTPStatus.OK
    assert response.context_data["rules"].count() == 0
    assert "rules/rules_list.html" in response.template_name

    # One subscribed by client
    user.client.subscribed_rules.add(rule_a)
    response = create_response(user, url)
    assert response.status_code == http.HTTPStatus.OK
    assert rule_a.title in (
        response_entries := response.context_data["rules"].values_list("rule__title", flat=True)
    )
    assert response_entries.count() == 1
    assert "rules/rules_list.html" in response.template_name

    # Both subscribed by client
    user.client.subscribed_rules.add(rule_b)
    response = create_response(user, url)
    assert response.status_code == http.HTTPStatus.OK
    assert rule_a.title in (
        response_entries := response.context_data["rules"].values_list("rule__title", flat=True)
    )
    assert rule_b.title in response_entries
    assert response_entries.count() == 2
    assert "rules/rules_list.html" in response.template_name

    # Rule A deactivated
    user.client.rule_users.filter(rule__id=rule_a.pk).update(active=False)
    response = create_response(user, url)
    assert response.status_code == http.HTTPStatus.OK
    assert (
        response_entries := response.context_data["rules"].values_list("rule__title", flat=True)
    ).count() == 2
    assert response_entries[0] == rule_b.title
    assert response_entries[1] == rule_a.title

    # Rule A activated again
    user.client.rule_users.filter(rule__id=rule_a.pk).update(active=True)
    response = create_response(user, url)
    assert response.status_code == http.HTTPStatus.OK
    assert (
        response_entries := response.context_data["rules"].values_list("rule__title", flat=True)
    ).count() == 2
    assert response_entries[0] == rule_a.title
    assert response_entries[1] == rule_b.title


@pytest.mark.django_db
def test_rules_update_to_inactive_view(create_response):
    client = ClientFactory.create()
    rule = RuleFactory.create(title="A")
    rule_client = RuleClientFactory.create(client=client, rule=rule)
    url = reverse("rules:update_to_inactive", kwargs={"pk": rule_client.pk})
    assert rule_client.active is True

    response = create_response(client.user, url, method="POST")

    assert response.status_code == http.HTTPStatus.FOUND
    assert RuleClient.objects.get(pk=rule_client.pk).active is False

    # RuleClient object not belonging to this client is not set to inactive
    rule_client = RuleClientFactory.create(rule=rule)
    assert rule_client.active is True
    url = reverse("rules:update_to_inactive", kwargs={"pk": rule_client.pk})

    response = create_response(client.user, url, method="POST")

    assert response.status_code == http.HTTPStatus.FOUND
    assert RuleClient.objects.get(pk=rule_client.pk).active is True


@pytest.mark.django_db
def test_rules_update_to_active_view(create_response):
    client = ClientFactory.create()
    rule = RuleFactory.create(title="A")
    rule_client = RuleClientFactory.create(client=client, rule=rule, active=False)
    url = reverse("rules:update_to_active", kwargs={"pk": rule_client.pk})
    assert rule_client.active is False

    response = create_response(client.user, url, method="POST")

    assert response.status_code == http.HTTPStatus.FOUND
    assert RuleClient.objects.get(pk=rule_client.pk).active is True

    # RuleClient object not belonging to this client is not set to active
    rule_client = RuleClientFactory.create(rule=rule, active=False)
    assert rule_client.active is False
    url = reverse("rules:update_to_active", kwargs={"pk": rule_client.pk})

    response = create_response(client.user, url, method="POST")

    assert response.status_code == http.HTTPStatus.FOUND
    assert RuleClient.objects.get(pk=rule_client.pk).active is False
