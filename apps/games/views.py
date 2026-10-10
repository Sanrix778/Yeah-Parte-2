"""Vistas públicas del catálogo de juegos (spec §7.2)."""
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Category, Character, Game, GameStatus, Participant, WalkthroughSection


class GameListView(ListView):
    model = Game
    template_name = "games/list.html"
    context_object_name = "games"
    paginate_by = 24

    def get_queryset(self):
        qs = Game.objects.for_home().select_related("category")
        self.category = None

        cat_slug = self.request.GET.get("categoria")
        if cat_slug:
            self.category = get_object_or_404(Category, slug=cat_slug)
            qs = qs.filter(category=self.category)

        platform = self.request.GET.get("plataforma")
        if platform:
            qs = qs.filter(platform=platform)

        estado = self.request.GET.get("estado")
        if estado in dict(GameStatus.choices):
            qs = qs.filter(status=estado)

        query = self.request.GET.get("q", "").strip()
        if query:
            qs = qs.filter(title__icontains=query)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["selected_category"] = self.category
        ctx["q"] = self.request.GET.get("q", "")
        ctx["platforms"] = Game._meta.get_field("platform")
        return ctx


class GameDetailView(DetailView):
    model = Game
    template_name = "games/detail.html"
    context_object_name = "game"
    slug_field = "slug"

    def get_queryset(self):
        return Game.objects.published().select_related("category")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        game = self.object
        ctx["characters"] = Character.objects.filter(game=game)
        # Staff ve también las secciones en construcción; el público solo las públicas.
        sections = WalkthroughSection.objects.filter(game=game)
        if not self.request.user.is_staff:
            sections = sections.filter(is_public=True)
        ctx["sections"] = sections
        ctx["participants"] = Participant.objects.filter(game=game).select_related("user")
        ctx["tab"] = self.request.GET.get("tab", "info")
        ctx["game_tabs"] = [
            ("info", "Info"),
            ("characters", "Personajes"),
            ("guide", "Guía"),
            ("team", "Equipo"),
        ]
        ctx["related_comics"] = game.comics.filter(is_published=True)
        return ctx


class WalkthroughIndexView(DetailView):
    model = Game
    template_name = "games/walkthrough.html"
    context_object_name = "game"
    slug_field = "slug"

    def get_queryset(self):
        return Game.objects.published()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = WalkthroughSection.objects.filter(game=self.object)
        ctx["sections"] = qs if self.request.user.is_staff else qs.filter(is_public=True)
        return ctx


class WalkthroughDetailView(DetailView):
    model = WalkthroughSection
    template_name = "games/walkthrough_detail.html"
    context_object_name = "section"
    slug_field = "slug"

    def get_queryset(self):
        qs = WalkthroughSection.objects.select_related("game")
        if not self.request.user.is_staff:
            qs = qs.filter(is_public=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        siblings = WalkthroughSection.objects.filter(game=self.object.game).order_by("order")
        if not self.request.user.is_staff:
            siblings = siblings.filter(is_public=True)
        ctx["siblings"] = siblings
        ctx["page_image"] = self.object.game.card_image
        return ctx


class CategoryDetailView(ListView):
    model = Game
    template_name = "games/list.html"
    context_object_name = "games"
    paginate_by = 24

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return Game.objects.for_home().filter(category=self.category)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["selected_category"] = self.category
        return ctx