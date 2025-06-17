from django.urls import path
from .views import TranslateWordView, UserTranslationsByUUID

urlpatterns = [
    path(
        "translate/",
        TranslateWordView.as_view(),
        name="translate-word",
    ),
    path(
        "user-translations-by-uuid/<uuid:uuid>/",
        UserTranslationsByUUID.as_view(),
        name="user-translations-by-uuid",
    ),
]
