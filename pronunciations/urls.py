from django.urls import path
from .views import Pronunciations

urlpatterns = [
    path(
        "pronunciations/",
        Pronunciations.as_view(),
        name="pronunciations",
    ),
]
