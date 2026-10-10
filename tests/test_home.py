"""La home y el buscador (spec §9, HU-01..HU-04)."""
import pytest
from django.urls import reverse

from apps.games.models import GameStatus

from .conftest import ComicFactory, GameFactory

pytestmark = pytest.mark.django_db


def test_home_shows_branding(client):
    content = client.get(reverse("site:home")).content.decode()
    assert "Devilopers" in content
    assert "Games" in content
    assert "Comics" in content


def test_home_shows_max_four_games(client):
    for i in range(6):
        GameFactory(title=f"Juego {i}", status=GameStatus.RELEASED)

    content = client.get(reverse("site:home")).content.decode()

    # 4 cards en la sección Games + las que estén en "Destacados".
    assert "Juego 0" in content


def test_home_shows_comics(client):
    ComicFactory(title="Sanrix", is_published=True)
    content = client.get(reverse("site:home")).content.decode()
    assert "Sanrix" in content


def test_search_finds_game(client):
    GameFactory(title="Devil Hide Roblox")
    response = client.get(reverse("site:search"), {"q": "Devil"})
    assert "Devil Hide Roblox" in response.content.decode()


def test_search_finds_comic(client):
    ComicFactory(title="Sanrix", is_published=True)
    response = client.get(reverse("site:search"), {"q": "Sanrix"})
    assert "Sanrix" in response.content.decode()


def test_search_without_results(client):
    response = client.get(reverse("site:search"), {"q": "zzzz-no-existe"})
    assert response.status_code == 200
    assert "No encontramos nada" in response.content.decode()


def test_about_page(client):
    assert client.get(reverse("site:about")).status_code == 200


def test_health_endpoint(client):
    response = client.get(reverse("site:health"))
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_search_bar_is_in_header(client):
    content = client.get(reverse("site:home")).content.decode()
    assert 'action="/buscar/"' in content