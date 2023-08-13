from django.contrib.auth import views as auth_views
from django.urls import path
from users import views

app_name = "users"

urlpatterns = [
    path("index/", views.index, name="index"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path(
        "perform_logout/",
        auth_views.LogoutView.as_view(next_page="users:login"),
        name="perform_logout",
    ),
    path("profile/", views.ProfilePageView.as_view(), name="profile"),
    path("change_password/", views.CustomPasswordChangeView.as_view(), name="change_password"),
    path("<int:pk>/change_email/", views.EmailUpdateView.as_view(), name="change_email"),
    path(
        "password_change_done/",
        auth_views.PasswordChangeDoneView.as_view(template_name="users/password_change_done.html"),
        name="password_change_done",
    ),
]
