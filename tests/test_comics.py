"""Listado, capítulos y páginas del cómic (spec §9)."""
import pytest
from django.urls import reverse

from apps.comics.models import ComicPage

from .conftest import ComicChapterFactory, ComicFactory, ComicPageFactory

pytestmark = pytest.mark.django_db


def test_only_published_comics_are_listed(client):
    ComicFactory(title="Sanrix", is_published=True)
    ComicFactory(title="Comic Secreto", is_published=False)

    content = client.get(reverse("comics:list")).content.decode()

    assert "Sanrix" in content
    assert "Comic Secreto" not in content


def test_comic_detail_lists_published_chapters(client):
    comic = ComicFactory()
    ComicChapterFactory(comic=comic, number=1, title="Chapter 1")
    ComicChapterFactory(comic=comic, number=2, slug="sin-fecha", published_at=None)

    content = client.get(reverse("comics:detail", args=[comic.slug])).content.decode()

    assert "Chapter 1" in content
    assert "sin-fecha" not in content


def test_reader_shows_pages_in_order(client):
    comic = ComicFactory()
    chapter = ComicChapterFactory(comic=comic)
    ComicPageFactory(order=0, alt_text="Primera")
    ComicPageFactory(order=1, alt_text="Segunda")
    ComicPageFactory(order=2, alt_text="Tercera")
    chapter.pages.add(*ComicPage.objects.all())

    response = client.get(reverse("comics:reader", args=[comic.slug, chapter.slug]))
    content = response.content.decode()

    assert response.status_code == 200
    assert content.index("Primera") < content.index("Segunda") < content.index("Tercera")


def test_reader_navigates_between_chapters(client):
    comic = ComicFactory()
    ComicChapterFactory(comic=comic, number=1, slug="c1")
    ComicChapterFactory(comic=comic, number=2, slug="c2")
    ComicChapterFactory(comic=comic, number=3, slug="c3")

    content = client.get(reverse("comics:reader", args=[comic.slug, "c2"])).content.decode()

    assert "/comics/%s/c1/" % comic.slug in content  # anterior
    assert "/comics/%s/c3/" % comic.slug in content  # siguiente


def test_first_chapter_has_no_previous(client):
    comic = ComicFactory()
    ComicChapterFactory(comic=comic, number=1, slug="c1")
    ComicChapterFactory(comic=comic, number=2, slug="c2")

    content = client.get(reverse("comics:reader", args=[comic.slug, "c1"])).content.decode()

    assert "/comics/%s/c2/" % comic.slug in content


def test_empty_chapter_returns_200_not_500(client):
    comic = ComicFactory()
    chapter = ComicChapterFactory(comic=comic)

    response = client.get(reverse("comics:reader", args=[comic.slug, chapter.slug]))

    assert response.status_code == 200
    assert "todavía no tiene páginas" in response.content.decode()


def test_unpublished_chapter_is_404_for_public(client):
    comic = ComicFactory()
    chapter = ComicChapterFactory(comic=comic, published_at=None)

    response = client.get(reverse("comics:reader", args=[comic.slug, chapter.slug]))

    assert response.status_code == 404


def test_home_shows_at_most_two_comics(client):
    for i in range(4):
        ComicFactory(title=f"Comic {i}", is_published=True)

    content = client.get(reverse("site:home")).content.decode()

    assert content.count("comics/") >= 2