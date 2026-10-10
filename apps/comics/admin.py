"""Admin del cómic (spec §7)."""
from django.contrib import admin

from .models import Comic, ComicChapter, ComicPage


class ComicChapterInline(admin.TabularInline):
    model = ComicChapter
    extra = 0
    fields = ("number", "title", "slug", "pages", "published_at")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Comic)
class ComicAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "game", "chapter_count", "created_at")
    list_filter = ("is_published",)
    list_editable = ("is_published",)
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ComicChapterInline]

    @admin.display(description="capítulos")
    def chapter_count(self, obj):
        return obj.chapters.count()


@admin.register(ComicChapter)
class ComicChapterAdmin(admin.ModelAdmin):
    list_display = ("comic", "number", "title", "published_at", "page_count")
    list_filter = ("comic",)
    ordering = ("comic", "number")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("pages",)

    @admin.display(description="páginas")
    def page_count(self, obj):
        return obj.pages.count()


@admin.register(ComicPage)
class ComicPageAdmin(admin.ModelAdmin):
    list_display = ("__str__", "alt_text", "order")
    list_editable = ("order",)