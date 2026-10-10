"""Copia los assets de `Imagenes/` a `MEDIA_ROOT` para que el seed los encuentre.

Uso:  python manage.py setup_seed_assets

El repo tiene las imágenes en `Imagenes/` (material de trabajo del equipo) pero
Django sirve los archivos de `media/`. Este comando copia las que el sitio
necesita, sin tocar los originales.

Los thumbnails de las cards vienen de los screenshots de `Imagenes/Iconos/`.
"""
from pathlib import Path
from shutil import copy2

from django.conf import settings
from django.core.management.base import BaseCommand

# (origen relativo a BASE_DIR, destino relativo a MEDIA_ROOT)
COPIES = [
    ("Imagenes/SanrixBlox.png", "comics/covers/sanrix.png"),
    ("Imagenes/SanrixBlox_alt2.png", "comics/covers/sanrix-alt2.png"),
    # Placeholder para juegos sin portada real todavía. Se reemplaza desde el
    # admin cuando haya arte definitivo de cada juego.
    ("Imagenes/Iconos/icon.png", "games/covers/placeholder.png"),
]


class Command(BaseCommand):
    help = "Copia las imágenes iniciales de Imagenes/ a MEDIA_ROOT."

    def handle(self, *args, **options):
        base = Path(settings.BASE_DIR)
        media = Path(settings.MEDIA_ROOT)
        copied = 0
        missing = []

        for src_rel, dst_rel in COPIES:
            src = base / src_rel
            dst = media / dst_rel
            if not src.exists():
                missing.append(src_rel)
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            copy2(src, dst)
            copied += 1
            self.stdout.write(f"  {src_rel} -> media/{dst_rel}")

        self.stdout.write(self.style.SUCCESS(f"Copiados: {copied}"))
        if missing:
            self.stdout.write(
                self.style.WARNING(
                    "No encontrados (se cargan desde el admin): " + ", ".join(missing)
                )
            )