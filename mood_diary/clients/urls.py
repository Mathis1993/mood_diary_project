from clients import views
from django.urls import path

app_name = "clients"

urlpatterns = [
    path("create/", views.CreateClientView.as_view(), name="create_client"),
    path("get_all/", views.ClientListView.as_view(), name="list_clients"),
]
