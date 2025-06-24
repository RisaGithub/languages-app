from django.urls import path
from .views import TranslateWordForUserView

urlpatterns = [
    path(
        "translate-for-user/",
        TranslateWordForUserView.as_view(),
        name="translate-word-for-user",
    ),
]
