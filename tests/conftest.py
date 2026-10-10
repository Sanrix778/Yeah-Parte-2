"""Factories compartidas para los tests (spec §9)."""
import io

import factory
from django.core.files.images import ImageFile
from django.utils import timezone
from PIL import Image

from apps.accounts.models import User
from apps.comics.models import Comic, ComicChapter, ComicPage
from apps.games.models import (
    Category,
    Character,
    Game,
    GameStatus,
    Participant,
    Platform,
    WalkthroughSection,
)


def make_image(name="test.png", size=(64, 64), color=(255, 0, 0)):
    """PNG válido en memoria, para los ImageField."""
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    buf.seek(0)
    return ImageFile(buf, name=name)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"jugador{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@devilopers.test")
    password = factory.PostGenerationMethodCall("set_password", "clave-de-prueba")

    @factory.post_generation
    def avatar(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.avatar = make_image("avatar.png", (32, 32))


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Categoría {n}")
    slug = factory.Sequence(lambda n: f"categoria-{n}")


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Game

    title = factory.Sequence(lambda n: f"Juego {n}")
    slug = factory.Sequence(lambda n: f"juego-{n}")
    platform = Platform.WEB
    category = factory.SubFactory(CategoryFactory)
    about = factory.Faker("paragraph", nb_sentences=3)
    origin = factory.Faker("paragraph", nb_sentences=2)
    status = GameStatus.RELEASED
    order = factory.Sequence(lambda n: n)
    cover_image = factory.LazyAttribute(lambda o: make_image("cover.png"))

    @factory.post_generation
    def thumbnail(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.thumbnail = make_image("thumb.png")


class CharacterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Character

    game = factory.SubFactory(GameFactory)
    name = factory.Sequence(lambda n: f"Personaje {n}")
    slug = factory.Sequence(lambda n: f"personaje-{n}")
    role = "protagonista"


class ParticipantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Participant

    game = factory.SubFactory(GameFactory)
    display_name = factory.Sequence(lambda n: f"Dev {n}")
    role = "art"


class WalkthroughSectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WalkthroughSection

    game = factory.SubFactory(GameFactory)
    title = factory.Sequence(lambda n: f"Sección {n}")
    slug = factory.Sequence(lambda n: f"seccion-{n}")
    content = "Contenido de prueba."
    is_public = True


class ComicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comic

    title = factory.Sequence(lambda n: f"Comic {n}")
    slug = factory.Sequence(lambda n: f"comic-{n}")
    is_published = True
    cover_image = factory.LazyAttribute(lambda o: make_image("comic.png"))


class ComicPageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComicPage

    image = factory.LazyAttribute(lambda o: make_image(f"page{o.order}.png", (400, 600)))
    alt_text = "Página de prueba"
    order = factory.Sequence(lambda n: n)


class ComicChapterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComicChapter

    comic = factory.SubFactory(ComicFactory)
    number = 1
    slug = factory.Sequence(lambda n: f"capitulo-{n}")
    published_at = factory.LazyAttribute(lambda o: timezone.now())