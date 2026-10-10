"""El walkthrough se sanea: nada de HTML crudo del admin (spec §8, §9)."""
import pytest
from django.urls import reverse

from .conftest import GameFactory, WalkthroughSectionFactory

pytestmark = pytest.mark.django_db


def test_markdown_is_rendered(client):
    game = GameFactory()
    section = WalkthroughSectionFactory(game=game, content="# Título\n\nUn **negrita**.")
    response = client.get(section.get_absolute_url())
    content = response.content.decode()

    assert response.status_code == 200
    assert "<h1" in content
    assert "<strong>negrita</strong>" in content


def test_script_tag_is_stripped(client):
    game = GameFactory()
    section = WalkthroughSectionFactory(
        game=game, content="Antes <script>alert('xss')</script> después."
    )
    content = client.get(section.get_absolute_url()).content.decode()

    assert "<script>alert" not in content
    assert "Antes" in content and "después" in content


def test_onerror_attribute_is_stripped(client):
    game = GameFactory()
    section = WalkthroughSectionFactory(
        game=game, content='<img src="x" onerror="alert(1)">'
    )
    content = client.get(section.get_absolute_url()).content.decode()

    assert "onerror" not in content


def test_private_section_hidden_from_public(client):
    game = GameFactory()
    WalkthroughSectionFactory(game=game, title="Sección Privada", is_public=False)

    content = client.get(game.get_absolute_url()).content.decode()
    assert "Sección Privada" not in content


def test_staff_sees_private_section(client):
    from .conftest import UserFactory

    game = GameFactory()
    WalkthroughSectionFactory(game=game, title="Sección Privada", is_public=False)

    client.force_login(UserFactory(is_staff=True))
    content = client.get(game.get_absolute_url()).content.decode()

    assert "Sección Privada" in content


def test_walkthrough_index_lists_public_sections(client):
    game = GameFactory()
    WalkthroughSectionFactory(game=game, title="Pública", is_public=True)
    WalkthroughSectionFactory(game=game, title="Oculta", is_public=False)

    response = client.get(reverse("games:walkthrough", args=[game.slug]))

    assert "Pública" in response.content.decode()
    assert "Oculta" not in response.content.decode()