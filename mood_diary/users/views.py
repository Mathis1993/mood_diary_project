from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy


@login_required(login_url="users:login")
def logout_confirmation(request):
    return render(request, "users/logout.html")


@login_required(login_url="users:login")
def index(request):
    user = request.user
    print(user.last_login)
    print(user.is_superuser)
    if not (user.first_login_completed or user.is_superuser):
        print("here")
        return redirect("users:change_password")
    else:
        return HttpResponse("Hello, world.")


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy("users:password_change_done")

    def form_valid(self, form):
        # Save the new password
        response = super().form_valid(form)

        # Perform additional actions
        user = self.request.user
        user.first_login_completed = True
        user.save()

        return response
