# Devilopers

Portal web de los **Devilopers**: catálogo de juegos, personajes, guías y el
cómic de Sanrix.

- Especificación: [`docs/spec.md`](docs/spec.md)
- Guía de estilo visual: [`DESIGN.md`](DESIGN.md)

El diseño (oscuro, dibujado a mano, tipografía manuscrita) está definido en
`DESIGN.md` y su traducción a tokens CSS está en `static/css/input.css`.

---

## Arranque

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"

python manage.py migrate
python manage.py createsuperuser
python manage.py setup_seed_assets     # copia Imagenes/ -> media/
python manage.py seed_content          # 8 categorías + 4 juegos + 2 cómics

python manage.py runserver
```

En http://127.0.0.1:8000/ está la home. El admin está en `/admin/`.

### CSS

El diseño depende de Tailwind, que se compila aparte:

```bash
# otra terminal, en watch mode:
python manage.py tailwind
```

Mientras corra, los cambios en `static/css/input.css` se reflejan al recargar.

### Tests

```bash
pytest                    # 41 tests
pytest tests/test_walkthrough.py -v
```

---

## Estructura

```
Yeah-Parte-2/
├─ manage.py
├─ pyproject.toml           # deps + pytest + ruff
├─ config/                  # proyecto Django: settings base/dev/prod, urls, wsgi
├─ apps/
│  ├─ accounts/             # User custom, login por email o username
│  ├─ games/                # Category, Game, Character, WalkthroughSection, Participant
│  ├─ comics/               # Comic, ComicChapter, ComicPage
│  └─ site/                 # home, búsqueda, "conócenos", health, filtro markdownify
├─ templates/
│  ├─ base.html
│  ├─ partials/             # header, footer, campos de formulario
│  └─ components/           # game_card.html, comic_card.html
├─ static/{css,js,img}/
├─ media/                   # subidas del admin (ignorado por git, salvo seed)
├─ Imagenes/                # material de trabajo del equipo (origen de los assets)
├─ tests/
└─ docs/spec.md
```

`DevilWeb/` es el proyecto Django original (Django 4.2 sin apps). Ya no se usa:
todo vive en `config/` + `apps/`. Se puede borrar cuando quieras, junto con
`DevilWeb/db.sqlite3.bak-core`.

---

## Stack

| Capa | Qué se usa |
|---|---|
| Python | 3.9 |
| Django | 4.2 LTS |
| BD | SQLite en dev, PostgreSQL en prod (`config/settings/prod.py`) |
| CSS | Tailwind CSS v4 vía `django-tailwind` |
| JS | Vanilla ES modules, sin bundler |
| Tests | pytest + pytest-django + factory_boy |

**Sobre la versión de Django:** el spec pide Django 5.2 LTS, que necesita Python
≥ 3.10. Esta máquina tiene solo Python 3.9, así que el proyecto quedó en Django
4.2 LTS. El código no usa nada deprecado: para subir de versión hay que instalar
Python 3.13, recrear el venv y cambiar el pin en `pyproject.toml`. Está
detallado en `docs/spec.md` §2.1.

---

## Rutas

| URL | Qué es |
|---|---|
| `/` | Home: Games (4 cards) + Comics (2 cards) |
| `/buscar/?q=` | Buscador de juegos y cómics |
| `/juegos/` | Listado con filtros por categoría, plataforma y estado |
| `/juegos/<slug>/` | Detalle con tabs: Info │ Personajes │ Guía │ Equipo |
| `/juegos/<slug>/guia/` | Índice de la guía |
| `/comics/` | Listado de cómics |
| `/comics/<slug>/` | Cómic con sus capítulos |
| `/comics/<slug>/<slug>/` | Lector del capítulo |
| `/cuentas/` | Registro, login, perfil, contraseña |
| `/conocenos/` | "Conócenos más" |
| `/health/` | JSON para deploy |
| `/admin/` | Admin de Django |

---

## Cargar contenido

Todo el contenido se carga desde `/admin/`, sin tocar código:

- **Juegos** `/admin/games/game/`: el alta trae inlines de personajes, secciones
  de guía y créditos, así que un juego se arma en una sola pantalla.
- **Personajes** `/admin/games/character/`
- **Cómics** `/admin/comics/comic/`: los capítulos van como inline; las páginas se
  cargan en `/admin/comics/comicpage/` y después se asignan al capítulo.
- **Tokens/logros**: fuera de alcance en el MVP (spec §11.2).

Los juegos en `draft` no aparecen en el sitio. El orden en la home lo define el
campo `order`, no la fecha.

---

## Problemas frecuentes

**La página sale sin estilos.**
El CSS se compila aparte: corré `python manage.py tailwind` en otra terminal.

**`403 Forbidden` al ver /cuentas/perfil/**
Necesitás estar logueado.

**Quiero empezar de cero con la base.**
`db.sqlite3` no está en git. `python manage.py setup_seed_assets` +
`python manage.py seed_content` reconstruyen el contenido.