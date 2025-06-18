from django.urls import path
from .views import TranslateWordView

urlpatterns = [
    path(
        "translate/",
        TranslateWordView.as_view(),
        name="translate-word",
    ),
]
