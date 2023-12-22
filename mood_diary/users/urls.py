"""
URL patterns for the users app.
"""

from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from users import views
from users.forms import CustomPasswordResetForm, CustomSetPasswordForm

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
    # Because the email address is used to encrypt the mood diary entry detail field,
    # we disable the possibility to change the email address for now.
    # path("<int:pk>/change_email/", views.EmailUpdateView.as_view(), name="change_email"),
    path(
        "password_change_done/",
        auth_views.PasswordChangeDoneView.as_view(template_name="users/password_change_done.html"),
        name="password_change_done",
    ),
    path(
        "reset_password/",
        auth_views.PasswordResetView.as_view(
            email_template_name="users/password_reset_email.html",
            from_email=settings.FROM_EMAIL,
            template_name="users/password_reset.html",
            success_url=reverse_lazy("users:password_reset_done"),
            form_class=CustomPasswordResetForm,
        ),
        name="reset_password",
    ),
    path(
        "reset_password_sent/",
        auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            form_class=CustomSetPasswordForm,
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset_password_complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "toggle_push_notifications/",
        views.TogglePushNotificationsView.as_view(),
        name="toggle_push_notifications",
    ),
]
