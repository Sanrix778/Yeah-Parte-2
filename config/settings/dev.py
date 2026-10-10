"""Configuración de desarrollo local: SQLite, DEBUG y emails a consola."""
from .base import *  # noqa: F401,F403
from .base import BASE_DIR

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "[::1]"]

# SQLite. Ver spec §2.1: es la base del MVP y no se migra ahora.
# `foreign_keys=ON` ya lo activa Django solo; WAL se activa en apps/site/apps.py
# mediante la señal connection_created (Django 4.2 no soporta init_command).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {"timeout": 20},
    }
}

# whitenoise con checksum para recargar sin collectstatic en dev.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# El login se crea a mano en dev; en prod se limita por IP.
AXES_ENABLED = False

# En dev, /static/ sirve los .png sueltos del repo para poder iterar el mockup.
import os  # noqa: E402

if os.environ.get("SERVE_REPO_IMAGES") == "1":
    STATICFILES_DIRS.append(BASE_DIR / "Imagenes")