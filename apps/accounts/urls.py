from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = "accounts"

# Estas rutas se montan bajo `path("cuentas/", ...)` en config/urls.py,
# así que aquí van SIN el prefijo `cuentas/`.
urlpatterns = [
    path("registro/", views.SignupView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("perfil/", views.ProfileView.as_view(), name="profile"),
    path(
        "password/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            success_url=reverse_lazy("accounts:password_change_done"),
        ),
        name="password_change",
    ),
    path(
        "password/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html",
        ),
        name="password_change_done",
    ),
]