"""Formularios de cuentas (spec §7, HU-09..HU-11)."""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        required=True,
        help_text="Es el único que se muestra en tu perfil.",
    )

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese email.")
        return email


class LoginForm(AuthenticationForm):
    """El campo `username` acepta email o username (ver backends.py)."""

    username = forms.CharField(label="Email o usuario")