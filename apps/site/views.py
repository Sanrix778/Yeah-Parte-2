"""Vistas públicas del sitio: home, búsqueda, "conócenos" y health (spec §7.1)."""
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import TemplateView

from apps.comics.models import Comic
from apps.games.models import Game


class HomeView(TemplateView):
    template_name = "site/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # El orden de la home es editorial (`order` + `featured`), no cronológico.
        ctx["games"] = (
            Game.objects.for_home().select_related("category").order_by("order", "title")[:4]
        )
        ctx["comics"] = (
            Comic.objects.filter(is_published=True).prefetch_related("chapters")[:2]
        )
        ctx["featured_games"] = (
            Game.objects.for_home().filter(featured=True).select_related("category")
        )
        return ctx


class SearchView(TemplateView):
    template_name = "site/search.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        ctx["q"] = query
        ctx["games"] = []
        ctx["comics"] = []
        if query:
            ctx["games"] = Game.objects.for_home().filter(
                Q(title__icontains=query)
                | Q(tagline__icontains=query)
                | Q(about__icontains=query)
            ).select_related("category")[:20]
            ctx["comics"] = Comic.objects.filter(is_published=True).filter(
                Q(title__icontains=query)
                | Q(tagline__icontains=query)
                | Q(description__icontains=query)
            )[:20]
        return ctx


class AboutView(TemplateView):
    template_name = "site/about.html"


def health(request):
    """Endpoint para deploy. Verifica que la DB responde."""
    try:
        Game.objects.exists()
    except Exception:
        return JsonResponse({"status": "error", "db": "unavailable"}, status=503)
    return JsonResponse({"status": "ok", "db": "ok"})