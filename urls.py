from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("ai/", include("ai.urls")),
    path("admin/", admin.site.urls),
]