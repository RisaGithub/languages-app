from django.contrib import admin
from django.urls import path, include
from users.views import CreateAnonymousUserView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/words/", include("words.urls")),
    path(
        "api/create-anonymous/",
        CreateAnonymousUserView.as_view(),
        name="create_anonymous_user",
    ),
]
