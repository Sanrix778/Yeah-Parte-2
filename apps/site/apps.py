from django.apps import AppConfig
from django.db.backends.signals import connection_created
from django.dispatch import receiver
from tailwind.apps import TailwindConfig


class SiteConfig(TailwindConfig):
    """Contiene la home y el CSS de Tailwind (django-tailwind usa esta app)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.site"
    label = "site"
    verbose_name = "Sitio"

    def ready(self):
        register_sqlite_pragmas()


def register_sqlite_pragmas():
    """Activa WAL en SQLite.

    Django 4.2 no soporta la opción `init_command` del backend sqlite3 (se
    agregó en 5.1), así que el pragma se aplica al abrir cada conexión.
    WAL reduce los bloqueos entre el runserver y el build de Tailwind.
    """

    @receiver(connection_created)
    def _set_sqlite_pragmas(sender, connection, **kwargs):
        if connection.vendor != "sqlite":
            return
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")