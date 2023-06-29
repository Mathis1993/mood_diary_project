from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy

User = get_user_model()


@login_required(login_url="users:login")
def index(request: HttpRequest) -> HttpResponse:
    user = request.user
    if not (user.first_login_completed or user.is_superuser):
        return redirect("users:change_password")

    if user.role == User.Role.ADMIN:
        return redirect("admin:index")

    if user.role == User.Role.COUNSELOR:
        return redirect("dashboards:dashboard_counselor")

    if user.role == User.Role.CLIENT:
        return redirect("dashboards:dashboard_client")


class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["username"].widget.attrs.update(
            {
                "class": "form-control form-control-user",
                "aria-describedby": "emailHelp",
                "placeholder": "Enter Email Address...",
            }
        )
        form.fields["password"].widget.attrs.update(
            {
                "class": "form-control form-control-user",
                "placeholder": "Enter Password...",
            }
        )
        return form


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:index")

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.request.user
        user.first_login_completed = True
        user.save()

        return response

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["old_password"].widget.attrs.update(
            {
                "class": "form-control form-control-user",
                "placeholder": "Enter Old Password...",
            }
        )
        form.fields["new_password1"].widget.attrs.update(
            {
                "class": "form-control form-control-user",
                "placeholder": "Enter New Password...",
            }
        )
        form.fields["new_password2"].widget.attrs.update(
            {
                "class": "form-control form-control-user",
                "placeholder": "Confirm New Password...",
            }
        )
        return form
