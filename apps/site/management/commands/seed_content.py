"""Carga el contenido inicial del portal (spec §1.2).

Uso:  python manage.py seed_content

Crea las categorías y los 4 juegos del mockup (Devil Hide Roblox, Devil Hide en
Web, Test Place, Cookie - Clicker) más el cómic de Sanrix con sus 2 capítulos.

No toca los archivos de `Imagenes/`: las imágenes se referencian por ruta
dentro de MEDIA_ROOT y se resuelven en un paso aparte (setup_seed_assets), para
que este comando se pueda correr las veces que haga falta.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.comics.models import Comic, ComicChapter
from apps.games.models import Category, Game, GameStatus, Platform

CATEGORIES = [
    ("Acción", "#9e1717", "Acción directa y combate."),
    ("Supervivencia", "#3f6212", "Sobrevivir un poco más cada ronda."),
    ("Terror", "#4c1d95", "Lo que pasa de noche en Devil Hide."),
    ("Puzzle", "#0e7490", "Escarabellas y cosas que se thinking."),
    ("Clicker", "#ca8a04", "Hacé click. Eso es todo."),
    ("Herramienta", "#6b7280", "Cosas queerno son un juego del todo."),
    ("Web", "#1d4ed8", "Juegos que corren en el navegador."),
    ("Otro", "#6b7280", "Lo que no entra en ninguna categoría."),
]

# (título, slug, plataforma, tagline, categoría, estado, orden, destacado)
GAMES = [
    {
        "title": "Devil Hide Roblox",
        "platform": Platform.ROBLOX,
        "category": "Terror",
        "tagline": "Aguantá la noche. Escondete de los demonios.",
        "about": "Devil Hide es nuestro juego de terror y supervivencia en Roblox. "
        "De noche aparecen cosas que no deberían estar, y la única forma de "
        "llegar al amanecer es esconderse.",
        "origin": "La idea salió de una ronda de Minecraft de madrugada. Uno dijo "
        '"que el mundo se ducked solo de noche" y todos entendimos a qué hora nos '
        "íbamos a dormir.",
        "status": GameStatus.RELEASED,
        "order": 1,
        "featured": True,
        "engine": "Roblox Studio",
        "cover": "games/covers/placeholder.png",
    },
    {
        "title": "Devil Hide en Web",
        "platform": Platform.WEB,
        "category": "Web",
        "tagline": "El mismo terror, directo en el navegador.",
        "about": "La versión web de Devil Hide, hecha para que la jugues sin instalar "
        "nada. Mismo miedo, menos descargas.",
        "origin": "Queríamos que cualquiera Pudiese probar el juego desde un link "
        "antes deINSTALLarlo. Salió de un fin de semana de peleas con el teclado.",
        "status": GameStatus.RELEASED,
        "order": 2,
        "featured": True,
        "engine": "Web (JavaScript)",
        "cover": "games/covers/placeholder.png",
    },
    {
        "title": "Test Place",
        "platform": Platform.ROBLOX,
        "category": "Herramienta",
        "tagline": "Donde probamos todo antes de romperlo en serio.",
        "about": "Un lugar de pruebas. Acá metemos las mecánicas nuevas, los "
        "mapas y las ideas a medio camino antes de meterlas en un juego real.",
        "origin": "Necesitábamos un lugar donde romper cosas sin romper el juego. "
        "Lo que era un scratch hoy es un mapa entero.",
        "status": GameStatus.UPCOMING,
        "order": 3,
        "featured": False,
        "engine": "Roblox Studio",
        "cover": "games/covers/placeholder.png",
    },
    {
        "title": "Cookie - Clicker",
        "platform": Platform.WEB,
        "category": "Clicker",
        "tagline": "Hacé click. Y después hacé más click.",
        "about": "Un clicker. Hacés click, juntás cookies, comprás más click. "
        "La premisa completa del juego es esa.",
        "origin": "Era un joke entre nosotros hasta que alguien lo encontró demasiado "
        "divertido y lo dejo funcionando. Ahora está acá.",
        "status": GameStatus.UPCOMING,
        "order": 4,
        "featured": False,
        "engine": "Web (JavaScript)",
        "cover": "games/covers/placeholder.png",
    },
]

# (comic slug, título, tagline, portada, [(número, título, slug)])
COMICS = [
    {
        "slug": "sanrix",
        "title": "SAN RIX",
        "tagline": "Dos tipos, una hell island y demasiados secretos.",
        "cover": "comics/covers/sanrix-alt2.png",
        "chapters": [
            (1, "Chapter 1", "chapter-1"),
        ],
    },
    {
        "slug": "sanrix-cuadros",
        "title": "SAN RIX",
        "tagline": "El comienzo de todo.",
        "cover": "comics/covers/sanrix.png",
        "chapters": [
            (1, "", "cuadros-1"),
        ],
    },
]


def _placeholder_image(path):
    """Devuelve una ImageField o, si el archivo no existe, cadena vacía.

    El seed corre en cualquier máquina: si el asset todavía no se copió a
    MEDIA_ROOT, el registro se crea igual y la imagen se sube después desde el
    admin (ImageField no tiene default, así que usamos None explícito).
    """
    from django.conf import settings

    full = settings.MEDIA_ROOT / path
    return path if full.exists() else None


class Command(BaseCommand):
    help = "Carga categorías, juegos y cómics iniciales del portal Devilopers."

    def handle(self, *args, **options):
        cats = {}
        for name, color, description in CATEGORIES:
            category, _ = Category.objects.update_or_create(
                slug=slugify(name, allow_unicode=False),
                defaults={
                    "name": name,
                    "accent_color": color,
                    "description": description,
                },
            )
            cats[name] = category
        self.stdout.write(f"Categorías: {len(cats)}")

        games = []
        for data in GAMES:
            cover = _placeholder_image(data["cover"])
            game, created = Game.objects.update_or_create(
                slug=slugify(data["title"]),
                defaults={
                    "title": data["title"],
                    "platform": data["platform"],
                    "category": cats[data["category"]],
                    "tagline": data["tagline"],
                    "about": data["about"],
                    "origin": data["origin"],
                    "status": data["status"],
                    "order": data["order"],
                    "featured": data["featured"],
                    "engine": data["engine"],
                    "released_at": (
                        "2025-12-16" if data["status"] == GameStatus.RELEASED else None
                    ),
                    "meta_description": data["tagline"][:160],
                },
            )
            if cover:
                game.cover_image.name = cover
                game.save(update_fields=["cover_image"])
            games.append(game)
        self.stdout.write(f"Juegos: {len(games)}")

        comics = []
        for data in COMICS:
            cover = _placeholder_image(data["cover"])
            comic, _ = Comic.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "tagline": data["tagline"],
                    "description": "",
                    "is_published": True,
                },
            )
            if cover:
                comic.cover_image.name = cover
                comic.save(update_fields=["cover_image"])
            for number, title, chapter_slug in data["chapters"]:
                ComicChapter.objects.update_or_create(
                    comic=comic,
                    number=number,
                    defaults={
                        "title": title,
                        "slug": chapter_slug,
                        # sin páginas: se cargan desde el admin
                    },
                )
            comics.append(comic)
        self.stdout.write(f"Cómics: {len(comics)}")

        self.stdout.write(self.style.SUCCESS("Contenido inicial cargado."))
        self.stdout.write(
            "Las páginas de los capítulos se cargan desde el admin: "
            "/admin/comics/comicchapter/"
        )