"""Modelos del cómic de Sanrix (spec §3.7–§3.8)."""
from django.db import models


class Comic(models.Model):
    """Una historieta del equipo. `game` es opcional para permitir crossover."""

    title = models.CharField("título", max_length=140)
    slug = models.SlugField("slug", unique=True)
    tagline = models.CharField("frase", max_length=180, blank=True)
    description = models.TextField("descripción", blank=True)
    cover_image = models.ImageField("portada", upload_to="comics/covers/")
    game = models.ForeignKey(
        "games.Game",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comics",
        verbose_name="juego relacionado",
    )
    is_published = models.BooleanField("publicado", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "cómic"
        verbose_name_plural = "cómics"
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("comics:detail", kwargs={"slug": self.slug})

    @property
    def published_chapters(self):
        return self.chapters.filter(published_at__isnull=False)


class ComicPage(models.Model):
    """Una imagen del cómic, reutilizable entre capítulos (spec §3.8)."""

    image = models.ImageField("imagen", upload_to="comics/pages/")
    alt_text = models.CharField(
        "texto alternativo", max_length=160, blank=True, help_text="Accesibilidad"
    )
    order = models.PositiveSmallIntegerField("orden", default=0)

    class Meta:
        verbose_name = "página"
        verbose_name_plural = "páginas"
        ordering = ["order", "id"]

    def __str__(self):
        return f"Página {self.order + 1}"


class ComicChapter(models.Model):
    """Capítulo de un cómic, con sus páginas ordenadas."""

    comic = models.ForeignKey(
        Comic, on_delete=models.CASCADE, related_name="chapters", verbose_name="cómic"
    )
    number = models.PositiveSmallIntegerField("número")
    title = models.CharField("título", max_length=140, blank=True)
    slug = models.SlugField("slug")
    pages = models.ManyToManyField(
        ComicPage, related_name="chapters", blank=True, verbose_name="páginas"
    )
    published_at = models.DateTimeField("publicado el", null=True, blank=True)

    class Meta:
        verbose_name = "capítulo"
        verbose_name_plural = "capítulos"
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(fields=["comic", "number"], name="uniq_chapter_per_comic")
        ]

    def __str__(self):
        return f"{self.comic.title} #{self.number}"

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("comics:reader", kwargs={"comic_slug": self.comic.slug, "slug": self.slug})

    @property
    def ordered_pages(self):
        return self.pages.all().order_by("order", "id")

    @property
    def page_count(self):
        return self.pages.count()