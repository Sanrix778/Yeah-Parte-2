"""Vistas de cuentas (spec §7, HU-09..HU-11)."""
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import LoginForm, SignupForm
from .models import User


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("site:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            from django.shortcuts import redirect

            return redirect("site:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        # Hay dos backends configurados (spec §2.1), así que login() necesita
        # saber cuál usó el usuario.
        login(
            self.request,
            self.object,
            backend="apps.accounts.backends.UsernameOrEmailBackend",
        )
        return response


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    http_method_names = ["post", "options"]  # POST only (spec §8)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ("first_name", "last_name", "email", "avatar", "bio")
    template_name = "accounts/profile.html"

    def get_object(self, queryset=None):
        # Sin esto, un anónimo llegaría acá con AnonymousUser y el formulario
        # nobbe guardaría nada. LoginRequiredMixin lo corta antes (spec §8).
        return User.objects.get(pk=self.request.user.pk)