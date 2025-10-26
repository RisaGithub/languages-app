from django.urls import path
from .views import ImageURLs

urlpatterns = [
    path(
        "image-urls/",
        ImageURLs.as_view(),
        name="image-urls",
    ),
]
