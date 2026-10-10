"""Registro, login con email y perfil (spec §9)."""
import pytest
from django.urls import reverse

from .conftest import UserFactory

pytestmark = pytest.mark.django_db


def test_signup_creates_user_and_logs_in(client):
    response = client.post(
        reverse("accounts:signup"),
        {
            "username": "nuevo",
            "email": "nuevo@devilopers.test",
            "password1": "clave-larga-123",
            "password2": "clave-larga-123",
        },
    )

    assert response.status_code == 302
    assert client.session.get("_auth_user_id")


def test_signup_rejects_duplicate_email(client):
    UserFactory(email="repetido@devilopers.test")

    response = client.post(
        reverse("accounts:signup"),
        {
            "username": "otro",
            "email": "repetido@devilopers.test",
            "password1": "clave-larga-123",
            "password2": "clave-larga-123",
        },
    )

    assert response.status_code == 200
    assert "Ya existe una cuenta" in response.content.decode()


def test_login_with_username(client):
    UserFactory(username="sanrix", password="clave-larga-123")
    response = client.post(
        reverse("accounts:login"), {"username": "sanrix", "password": "clave-larga-123"}
    )
    assert response.status_code == 302


def test_login_with_email(client):
    UserFactory(username="sanrix", email="sanrix@devilopers.test", password="clave-larga-123")
    response = client.post(
        reverse("accounts:login"),
        {"username": "sanrix@devilopers.test", "password": "clave-larga-123"},
    )
    assert response.status_code == 302


def test_login_error_is_same_for_user_and_email(client):
    """Anti-enumeración: el mensaje no revela si el usuario existe (spec §8).

    Se comparan los errores de un usuario inexistente y de uno existente con
    contraseña incorrecta: tienen que ser idénticos. Solo se compara el texto
    del error, no el HTML entero, porque el token CSRF cambia en cada request.
    """
    UserFactory(username="sanrix", password="clave-larga-123")

    def errors_for(username, password):
        response = client.post(
            reverse("accounts:login"), {"username": username, "password": password}
        )
        assert response.status_code == 200  # re-renderiza el form, no redirige
        assert not client.session.get("_auth_user_id")
        return list(response.context["form"].non_field_errors())

    unknown = errors_for("noexiste", "mala")
    wrong_password = errors_for("sanrix", "mala")

    assert unknown == wrong_password
    assert unknown  # el mensaje de error no está vacío


def test_profile_requires_login(client):
    response = client.get(reverse("accounts:profile"))
    assert response.status_code == 302
    assert "/cuentas/login/" in response.url


def test_profile_updates_fields(client):
    user = UserFactory()
    client.force_login(user)

    response = client.post(
        reverse("accounts:profile"),
        {"first_name": "Sanrix", "last_name": "B", "email": "nuevo@devilopers.test", "bio": "Hola."},
    )

    assert response.status_code == 302
    user.refresh_from_db()
    assert user.first_name == "Sanrix"
    assert user.bio == "Hola."


def test_logout_is_post_only(client):
    UserFactory(username="sanrix", password="clave-larga-123")
    client.login(username="sanrix", password="clave-larga-123")
    assert client.session.get("_auth_user_id")

    assert client.get(reverse("accounts:logout")).status_code == 405

    assert client.post(reverse("accounts:logout")).status_code == 302
    assert not client.session.get("_auth_user_id")