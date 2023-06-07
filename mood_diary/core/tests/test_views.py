import http

import pytest
from core.views import AuthenticatedClientRoleMixin, AuthenticatedCounselorRoleMixin
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory
from django.urls import reverse
from django.views import View
from users.tests.factories import UserFactory


@pytest.mark.django_db
def test_authenticated_counselor_mixin(django_user_model):
    class MyView(AuthenticatedCounselorRoleMixin, View):
        def get(self, request):
            return "ok"

    view = MyView.as_view()
    request = RequestFactory().get("/")

    # Unauthenticated user
    request.user = AnonymousUser()

    response = view(request)

    assert response.status_code == http.HTTPStatus.FOUND
    assert reverse(settings.LOGIN_URL) in response.url

    # Client user
    client_user = UserFactory.create(role=django_user_model.Role.CLIENT)
    request.user = client_user

    with pytest.raises(PermissionDenied):
        view(request)

    # Counselor
    counselor = UserFactory.create(role=django_user_model.Role.COUNSELOR)
    request.user = counselor

    response = view(request)

    assert response == "ok"


@pytest.mark.django_db
def test_authenticated_client_mixin(django_user_model):
    class MyView(AuthenticatedClientRoleMixin, View):
        def get(self, request):
            return "ok"

    view = MyView.as_view()
    request = RequestFactory().get("/")

    # Unauthenticated user
    request.user = AnonymousUser()

    response = view(request)

    assert response.status_code == http.HTTPStatus.FOUND
    assert reverse(settings.LOGIN_URL) in response.url

    # Counselor
    counselor = UserFactory.create(role=django_user_model.Role.COUNSELOR)
    request.user = counselor

    with pytest.raises(PermissionDenied):
        view(request)

    # Client user
    client_user = UserFactory.create(role=django_user_model.Role.CLIENT)
    request.user = client_user

    response = view(request)

    assert response == "ok"
