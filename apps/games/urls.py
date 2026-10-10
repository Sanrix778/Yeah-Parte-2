from django.urls import path

from . import views

app_name = "games"

urlpatterns = [
    path("juegos/", views.GameListView.as_view(), name="list"),
    path("juegos/<slug:slug>/", views.GameDetailView.as_view(), name="detail"),
    path("juegos/<slug:slug>/guia/", views.WalkthroughIndexView.as_view(), name="walkthrough"),
    path(
        "juegos/<slug:game_slug>/guia/<slug:slug>/",
        views.WalkthroughDetailView.as_view(),
        name="walkthrough_detail",
    ),
    path("categorias/<slug:slug>/", views.CategoryDetailView.as_view(), name="category"),
]