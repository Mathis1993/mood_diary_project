from django.contrib.auth import views as auth_views
from django.urls import path
from users import views

app_name = "users"

urlpatterns = [
    path("index/", views.index, name="index"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.logout_confirmation, name="logout"),
    path(
        "perform_logout/",
        auth_views.LogoutView.as_view(next_page="users:login"),
        name="perform_logout",
    ),
    path("change_password/", views.CustomPasswordChangeView.as_view(), name="change_password"),
    path(
        "password_change_done/",
        auth_views.PasswordChangeDoneView.as_view(template_name="users/password_change_done.html"),
        name="password_change_done",
    ),
]
