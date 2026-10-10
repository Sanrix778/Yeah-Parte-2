"""Modelos del catálogo de juegos (spec §3.2–§3.6)."""
from django.conf import settings
from django.db import models


class Category(models.Model):
    """Categoría de juego. Catálogo cerrado y pequeño, editable por staff."""

    name = models.CharField("nombre", max_length=60, unique=True)
    slug = models.SlugField("slug", unique=True)
    description = models.CharField("descripción", max_length=200, blank=True)
    accent_color = models.CharField(
        "color de acento", max_length=7, default="#6b7280", help_text="HEX, ej: #9e1717"
    )

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["name"]

    def __str__(self):
        return self.name


class GameStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    UPCOMING = "upcoming", "Próximamente"
    RELEASED = "released", "Publicado"
    ARCHIVED = "archived", "Archivado"


class Platform(models.TextChoices):
    ROBLOX = "roblox", "Roblox"
    WEB = "web", "Web"
    PC = "pc", "PC"
    MOBILE = "mobile", "Móvil"
    OTHER = "other", "Otro"


class GameQuerySet(models.QuerySet):
    def published(self):
        """Juegos visibles en el sitio público (spec §3.3)."""
        return self.exclude(status=GameStatus.DRAFT)

    def for_home(self):
        return self.published().filter(status__in=[GameStatus.RELEASED, GameStatus.UPCOMING])


class Game(models.Model):
    """Un juego del equipo.

    Las variantes de una misma Franchicia son registros separados distinguished
    por `platform` (spec §3.3): "Devil Hide Roblox" y "Devil Hide en Web" son
    dos filas con distinto link, estado y thumbnail.
    """

    title = models.CharField("título", max_length=140)
    slug = models.SlugField("slug", unique=True)
    platform = models.CharField(
        "plataforma", max_length=16, choices=Platform.choices, default=Platform.WEB
    )
    tagline = models.CharField(
        "frase", max_length=180, blank=True, help_text="1 línea para la card"
    )
    about = models.TextField("de qué trata")
    origin = models.TextField(
        "por qué salió la idea", blank=True, help_text="Parte de la identidad del equipo"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="games",
        verbose_name="categoría",
    )
    cover_image = models.ImageField("portada", upload_to="games/covers/")
    thumbnail = models.ImageField(
        "miniatura",
        upload_to="games/thumbs/",
        blank=True,
        null=True,
        help_text="Recorte cuadrado para la card (1:1)",
    )
    accent_color = models.CharField(
        "color de acento", max_length=7, blank=True, help_text="HEX del borde/ficha"
    )
    external_url = models.URLField("link externo", blank=True)
    engine = models.CharField("motor", max_length=40, blank=True)
    status = models.CharField(
        "estado", max_length=16, choices=GameStatus.choices, default=GameStatus.DRAFT
    )
    released_at = models.DateField("fecha de salida", null=True, blank=True)
    featured = models.BooleanField("destacado", default=False)
    order = models.PositiveSmallIntegerField("orden en la home", default=0)
    meta_description = models.CharField("meta description", max_length=160, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = GameQuerySet.as_manager()

    class Meta:
        verbose_name = "juego"
        verbose_name_plural = "juegos"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("games:detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        return self.status != GameStatus.DRAFT

    @property
    def card_image(self):
        """La card usa el thumbnail cuadrado; si falta, cae a la portada."""
        return self.thumbnail or self.cover_image


class Character(models.Model):
    """Personaje de un juego (spec §3.4).

    Cuelga de un juego porque el mismo personaje puede aparecer en varios
    (juego + cómic); en ese caso hay una ficha por juego.
    """

    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name="characters", verbose_name="juego"
    )
    name = models.CharField("nombre", max_length=100)
    slug = models.SlugField("slug")
    role = models.CharField("rol", max_length=60, blank=True)
    description = models.TextField("descripción", blank=True)
    portrait = models.ImageField("retrato", upload_to="characters/", blank=True, null=True)
    color = models.CharField("color de ficha", max_length=7, default="#6b7280")
    order = models.PositiveSmallIntegerField("orden", default=0)

    class Meta:
        verbose_name = "personaje"
        verbose_name_plural = "personajes"
        ordering = ["order", "name"]
        constraints = [
            models.UniqueConstraint(fields=["game", "slug"], name="uniq_character_per_game")
        ]

    def __str__(self):
        return self.name


class WalkthroughSection(models.Model):
    """Sección navegable de la guía de un juego (spec §3.5)."""

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name="walkthrough_sections",
        verbose_name="juego",
    )
    title = models.CharField("título", max_length=140)
    slug = models.SlugField("slug")
    order = models.PositiveSmallIntegerField("orden", default=0)
    is_public = models.BooleanField(
        "pública", default=False, help_text="Desmarcar si la guía está en construcción"
    )
    content = models.TextField("contenido", blank=True, help_text="Markdown")

    class Meta:
        verbose_name = "sección de guía"
        verbose_name_plural = "secciones de guía"
        ordering = ["order", "title"]
        constraints = [
            models.UniqueConstraint(fields=["game", "slug"], name="uniq_guide_section_per_game")
        ]

    def __str__(self):
        return f"{self.game.title} · {self.title}"

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("games:walkthrough_detail", kwargs={"game_slug": self.game.slug, "slug": self.slug})


class TeamRole(models.TextChoices):
    LEAD = "lead", "Lead"
    CODE = "code", "Programación"
    ART = "art", "Arte"
    DESIGN = "design", "Diseño"
    AUDIO = "audio", "Audio"
    WRITING = "writing", "Escritura"
    QA = "qa", "QA"
    OTHER = "other", "Otro"


class Participant(models.Model):
    """Crédito de una persona en un juego (spec §3.6).

    `user` es opcional: alguien puede estar en los créditos sin tener cuenta.
    """

    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name="participants", verbose_name="juego"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="participations",
        verbose_name="usuario",
        null=True,
        blank=True,
    )
    display_name = models.CharField("nombre público", max_length=80)
    role = models.CharField(
        "rol", max_length=16, choices=TeamRole.choices, default=TeamRole.OTHER
    )
    credit_order = models.PositiveSmallIntegerField("orden en los créditos", default=0)

    class Meta:
        verbose_name = "participante"
        verbose_name_plural = "participantes"
        ordering = ["role", "credit_order", "display_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["game", "display_name", "role"], name="uniq_credit_per_game_role"
            )
        ]

    def __str__(self):
        return f"{self.display_name} ({self.get_role_display()})"