"""URLs raíz del portal Devilopers."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Cuentas: login/logout/registro/perfil (spec §6).
    path("cuentas/", include("apps.accounts.urls")),
    # Juegos: listado, detalle con tabs, categorías y guía (spec §6).
    path("", include("apps.games.urls")),
    # Comics: portada, detalle de cómic y lector de capítulos.
    path("", include("apps.comics.urls")),
    # Home, búsqueda, "conócenos" y health (spec §6).
    path("", include("apps.site.urls")),
]

# En dev las subidas del admin se sirven directo desde MEDIA_ROOT.
# El estático ya lo resuelve whitenoise + STATICFILES_DIRS.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)