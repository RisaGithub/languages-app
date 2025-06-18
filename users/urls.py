from django.urls import path
from .views import (
    CreateAnonymousUserView,
    AddUserTranslationView,
    UserTranslationsByUUID,
)

urlpatterns = [
    path(
        "create-anonymous/",
        CreateAnonymousUserView.as_view(),
        name="create_anonymous_user",
    ),
    path(
        "add-translation/",
        AddUserTranslationView.as_view(),
        name="add_user_translation",
    ),
    path(
        "user-translations-by-uuid/<uuid:uuid>/",
        UserTranslationsByUUID.as_view(),
        name="user-translations-by-uuid",
    ),
]
