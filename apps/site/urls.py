from django.urls import path

from . import views

app_name = "site"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("buscar/", views.SearchView.as_view(), name="search"),
    path("conocenos/", views.AboutView.as_view(), name="about"),
    path("health/", views.health, name="health"),
]