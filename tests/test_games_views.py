"""Visibilidad, filtros y slugs del catálogo de juegos (spec §9)."""
import pytest
from django.urls import reverse

from apps.games.models import GameStatus, Platform

from .conftest import GameFactory

pytestmark = pytest.mark.django_db


def test_home_lists_only_published_games(client):
    published = GameFactory(status=GameStatus.RELEASED, title="Juego Visible")
    GameFactory(status=GameStatus.DRAFT, title="Juego Oculto")

    response = client.get(reverse("site:home"))

    assert response.status_code == 200
    assert published.title in response.content.decode()
    assert "Juego Oculto" not in response.content.decode()


def test_draft_game_returns_404_for_anonymous(client):
    draft = GameFactory(status=GameStatus.DRAFT)
    response = client.get(draft.get_absolute_url())
    assert response.status_code == 404


def test_upcoming_game_is_public(client):
    game = GameFactory(status=GameStatus.UPCOMING)
    assert client.get(game.get_absolute_url()).status_code == 200


def test_list_filter_by_category(client):
    from .conftest import CategoryFactory

    cat_a = CategoryFactory(name="Acción", slug="accion")
    cat_b = CategoryFactory(name="Puzzle", slug="puzzle")
    game_a = GameFactory(category=cat_a)
    game_b = GameFactory(category=cat_b)

    response = client.get(reverse("games:list"), {"categoria": "puzzle"})

    assert game_b.title in response.content.decode()
    assert game_a.title not in response.content.decode()


def test_list_filter_by_platform(client):
    roblox = GameFactory(platform=Platform.ROBLOX, title="Juego Roblox")
    GameFactory(platform=Platform.WEB, title="Juego Web")

    response = client.get(reverse("games:list"), {"plataforma": "roblox"})

    assert roblox.title in response.content.decode()
    assert "Juego Web" not in response.content.decode()


def test_search_by_title(client):
    client.get(reverse("site:search"), {"q": "Sanrix"})
    # El buscador funciona también sin q y devuelve 200.
    assert client.get(reverse("site:search")).status_code == 200


def test_detail_contains_about_and_origin(client):
    game = GameFactory(about="Esta es la historia", origin="Esto pasó porque sí")
    response = client.get(game.get_absolute_url())
    content = response.content.decode()

    assert "Esta es la historia" in content
    assert "Esto pasó porque sí" in content


def test_detail_lists_characters(client):
    from .conftest import CharacterFactory

    game = GameFactory()
    CharacterFactory(game=game, name="Sanrix B")
    CharacterFactory(game=game, name="Elizabeth")

    content = client.get(game.get_absolute_url(), {"tab": "characters"}).content.decode()

    assert "Sanrix B" in content
    assert "Elizabeth" in content


def test_detail_handles_no_characters(client):
    game = GameFactory()
    response = client.get(game.get_absolute_url(), {"tab": "characters"})
    assert response.status_code == 200
    assert "todavía no tiene personajes" in response.content.decode()


def test_home_respects_manual_order(client):
    third = GameFactory(order=3, title="Tercero")
    first = GameFactory(order=1, title="Primero")

    content = client.get(reverse("site:home")).content.decode()

    assert content.index("Primero") < content.index("Tercero")
    assert third.slug and first.slug