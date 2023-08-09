"""
URL configuration for mood_diary project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import users.views
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", users.views.index, name="index"),
    path("admin/", admin.site.urls),
    path("", include("pwa.urls")),
    path("clients/", include("clients.urls", namespace="clients")),
    path("dashboards/", include("dashboards.urls", namespace="dashboards")),
    path("diaries/", include("diaries.urls", namespace="diaries")),
    path("notifications/", include("notifications.urls", namespace="notifications")),
    path("rules/", include("rules.urls", namespace="rules")),
    path("users/", include("users.urls", namespace="users")),
]
