"""Admin del catálogo de juegos (spec §7)."""
from django.contrib import admin

from .models import Category, Character, Game, Participant, WalkthroughSection


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "accent_color")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


class CharacterInline(admin.TabularInline):
    model = Character
    extra = 1
    fields = ("name", "role", "color", "portrait", "order")


class WalkthroughSectionInline(admin.TabularInline):
    model = WalkthroughSection
    extra = 0
    fields = ("title", "is_public", "order")
    prepopulated_fields = {"slug": ("title",)}


class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 0
    fields = ("display_name", "role", "user", "credit_order")


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("title", "platform", "category", "status", "featured", "order")
    list_filter = ("status", "platform", "featured", "category")
    list_editable = ("order", "featured")
    search_fields = ("title", "tagline", "about")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "slug", "platform", "category", "status")}),
        ("Textos", {"fields": ("tagline", "about", "origin", "meta_description")}),
        ("Imágenes", {"fields": ("cover_image", "thumbnail", "accent_color")}),
        ("Links y técnica", {"fields": ("external_url", "engine", "released_at")}),
        ("Home", {"fields": ("featured", "order")}),
        ("Fechas", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    inlines = [CharacterInline, WalkthroughSectionInline, ParticipantInline]


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ("name", "game", "role", "color", "order")
    list_filter = ("game",)
    search_fields = ("name", "role")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(WalkthroughSection)
class WalkthroughSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "game", "is_public", "order")
    list_filter = ("is_public", "game")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("display_name", "game", "role", "user", "credit_order")
    list_filter = ("role", "game")
    search_fields = ("display_name",)