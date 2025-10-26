from django.urls import path
from .views import Definitions

urlpatterns = [
    path(
        "definitions/",
        Definitions.as_view(),
        name="definitions",
    ),
]
