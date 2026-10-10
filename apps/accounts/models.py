"""Modelo de usuario del portal Devilopers (spec §3.1)."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Usuario custom. No hay UserProfile separado: los campos son 1:1 fijos.

    El login acepta `username` **o** `email` (ver backends.py).
    """

    email = models.EmailField("email address", unique=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField("biografía", max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        ordering = ["-created_at"]

    def __str__(self):
        return self.get_display_name()

    def get_absolute_url(self):
        """Destino tras login/registro: el perfil del usuario."""
        from django.urls import reverse

        return reverse("accounts:profile")

    def get_display_name(self):
        """Nombre visible en créditos y comentarios."""
        return self.get_full_name() or self.username

    @property
    def participations_count(self):
        return self.participations.count()