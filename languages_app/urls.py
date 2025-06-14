from django.contrib import admin
from django.urls import path, include
from .views import available_routes_view


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", available_routes_view),
    path("api/words/", include("words.urls")),
    path("api/users/", include("users.urls")),
]
