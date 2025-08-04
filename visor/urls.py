from django.urls import path

from visor.views import metadata_views

app_name = "visor"
urlpatterns = [
    path("", metadata_views.gallery, name="gallery"),
    path("edit/<str:filename>/", metadata_views.edit_metadata, name="edit"),
]
