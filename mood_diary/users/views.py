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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        base_template = (
            "base_client_role.html" if self.request.user.is_client() else "base_counselor_role.html"
        )
        context["base_template"] = base_template

        return context


@login_required(login_url="users:login")
def index(request: HttpRequest) -> HttpResponse:
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
    template_name = "users/login.html"


class CustomPasswordChangeView(
    LoginRequiredMixin, SetBaseTemplateBasedOnUserRoleMixin, PasswordChangeView
):
    form_class = CustomPasswordChangeForm
    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:index")

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.request.user
        user.first_login_completed = True
        user.save()

        return response


class ProfilePageView(LoginRequiredMixin, View):
    template_name = "users/profile.html"

    def get(self, request):
        base_template = (
            "base_client_role.html" if request.user.is_client() else "base_counselor_role.html"
        )

        context = {"base_template": base_template}

        return render(request, self.template_name, context)


class EmailUpdateView(LoginRequiredMixin, SetBaseTemplateBasedOnUserRoleMixin, UpdateView):
    model = User
    form_class = UserEmailForm
    template_name = "users/email_update.html"

    def get_success_url(self):
        return reverse_lazy("users:index")
