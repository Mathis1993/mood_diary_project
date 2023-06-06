from clients import views
from django.urls import path

app_name = "clients"

urlpatterns = [
    path("create_client/", views.CreateClientView.as_view(), name="create_client"),
]
