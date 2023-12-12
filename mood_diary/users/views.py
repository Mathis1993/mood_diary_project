from core.views import AuthenticatedClientRoleMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import UpdateView
from users.forms import CustomPasswordChangeForm, UserEmailForm

User = get_user_model()


class SetBaseTemplateBasedOnUserRoleMixin:
    """
    Mixin that sets the `base_template` context variable based on the user's role so that
    e.g. client and counselor users see different navigation bars.
    """

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        base_template = (
            "base_client_role.html" if self.request.user.is_client() else "base_counselor_role.html"
        )
        context["base_template"] = base_template

        return context


@login_required(login_url="users:login")
def index(request: HttpRequest) -> HttpResponse:
    """
    This view redirects the user to the appropriate page after login.
    If the user is a client, they are redirected to the client dashboard.
    If the user is a counselor, they are redirected to the list of clients.
    If the user is an admin, they are redirected to django's admin interface.
    In case the user has not completed the first login, they are redirected to the
    change password page.

    Parameters
    ----------
    request: HttpRequest

    Returns
    -------
    HttpResponse
        Redirects to the appropriate page.
    """
    user = request.user
    if not (user.first_login_completed or user.is_superuser):
        return redirect("users:change_password")

    if user.is_admin():
        return redirect("admin:index")

    if user.is_counselor():
        return redirect("clients:list_clients")

    if user.is_client():
        return redirect("dashboards:dashboard_client")


class CustomLoginView(LoginView):
    """
    This view handles the login of users.
    """

    template_name = "users/login.html"


class CustomPasswordChangeView(
    LoginRequiredMixin, SetBaseTemplateBasedOnUserRoleMixin, PasswordChangeView
):
    """
    This view handles the changing of passwords.
    """

    form_class = CustomPasswordChangeForm
    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:index")

    def form_valid(self, form: CustomPasswordChangeForm) -> HttpResponse:
        """
        If the submitted form is valid, set the `first_login_completed` flag to `True`,
        because the user now has chosen their own password.

        Parameters
        ----------
        form:CustomPasswordChangeForm

        Returns
        -------
        HttpResponse
            Redirects to the index url for the user role.
        """
        response = super().form_valid(form)

        user = self.request.user
        user.first_login_completed = True
        user.save()

        return response


class ProfilePageView(LoginRequiredMixin, View):
    """
    This view handles the profile page of users.
    """

    template_name = "users/profile.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Upon receiving a GET request, render the profile page.
        There is a distinction between client and counselor users
        because only client users can receive push notifications and
        thus configure them.

        Parameters
        ----------
        request: HttpRequest

        Returns
        -------
        HttpResponse
        """
        base_template = (
            "base_client_role.html"
            if (is_client := request.user.is_client())
            else "base_counselor_role.html"
        )
        notifications_enabled = (
            request.user.client.push_notifications_granted if is_client else None
        )
        context = {
            "base_template": base_template,
            "is_client": is_client,
            "notifications_enabled": notifications_enabled,
        }

        return render(request, self.template_name, context)


class EmailUpdateView(LoginRequiredMixin, SetBaseTemplateBasedOnUserRoleMixin, UpdateView):
    """
    This view handles the updating of the email address of users.
    """

    model = User
    form_class = UserEmailForm
    template_name = "users/email_update.html"
    success_url = reverse_lazy("users:index")


class TogglePushNotificationsView(AuthenticatedClientRoleMixin, View):
    """
    This view handles setting the `push_notifications_granted` flag of a client user.
    """

    template_name = "users/profile.html"

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Upon receiving a POST request, toggle the `push_notifications_granted` flag to
        the opposite of its current value.

        Parameters
        ----------
        request: HttpRequest

        Returns
        -------
        HttpResponse
            Redirects to the profile page.
        """
        client = request.user.client
        client.push_notifications_granted = not client.push_notifications_granted
        client.save()

        return redirect("users:profile")
