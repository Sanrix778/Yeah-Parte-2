"""Configuración de tests: pytest + Django.

Se separa de `config/settings/dev.py` para no arrastrar whitenoise, emails ni
el resto de cosas de desarrollo.

Lo importante: los tests usan un MEDIA_ROOT temporal. Los factories crean
ImageField reales, y sin esto ensucian `media/` con cientos de PNG huérfanos
(los que se ven en `media/games/covers/cover_*.png`).
"""
from .dev import *  # noqa: F401,F403

import tempfile

DEBUG = False

# Secretos falsos: los tests nunca mandan correo real ni sirven archivos reales.
SECRET_KEY = "test-secret-key-no-usar-en-prod"
ALLOWED_HOSTS = ["*", "testserver"]

# Las imágenes que crean los tests se van a un tempfile que se borra solo.
MEDIA_ROOT = tempfile.mkdtemp(prefix="devilweb-test-media-")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Logging a null: sin esto los 404 esperados ensucian la salida de pytest.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"null": {"class": "logging.NullHandler"}},
    "loggers": {
        "django.request": {"handlers": ["null"], "level": "ERROR", "propagate": False},
        "django.security": {"handlers": ["null"], "level": "ERROR", "propagate": False},
    },
}