"""Vistas del cómic (spec §7.3)."""
from django.views.generic import DetailView, ListView

from .models import Comic, ComicChapter


class ComicListView(ListView):
    model = Comic
    template_name = "comics/list.html"
    context_object_name = "comics"

    def get_queryset(self):
        return Comic.objects.filter(is_published=True).prefetch_related("chapters")


class ComicDetailView(DetailView):
    model = Comic
    template_name = "comics/detail.html"
    context_object_name = "comic"
    slug_field = "slug"

    def get_queryset(self):
        return Comic.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["chapters"] = self.object.published_chapters
        return ctx


class ComicReaderView(DetailView):
    model = ComicChapter
    template_name = "comics/reader.html"
    context_object_name = "chapter"
    slug_field = "slug"

    def get_queryset(self):
        qs = ComicChapter.objects.select_related("comic").prefetch_related("pages")
        if not self.request.user.is_staff:
            qs = qs.filter(published_at__isnull=False, comic__is_published=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        comic = self.object.comic
        chapters = list(comic.published_chapters)
        idx = next((i for i, c in enumerate(chapters) if c.pk == self.object.pk), None)
        ctx["comic"] = comic
        ctx["pages"] = self.object.ordered_pages
        # Ojo: idx == 0 es el primer capítulo (no hay anterior), pero idx es 0 y
        # no None. Hay que comparar contra None explícitamente.
        ctx["prev_chapter"] = chapters[idx - 1] if idx else None
        ctx["next_chapter"] = (
            chapters[idx + 1] if idx is not None and idx + 1 < len(chapters) else None
        )
        return ctx