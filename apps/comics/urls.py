from django.urls import path

from . import views

app_name = "comics"

urlpatterns = [
    path("comics/", views.ComicListView.as_view(), name="list"),
    path("comics/<slug:slug>/", views.ComicDetailView.as_view(), name="detail"),
    path(
        "comics/<slug:comic_slug>/<slug:slug>/",
        views.ComicReaderView.as_view(),
        name="reader",
    ),
]