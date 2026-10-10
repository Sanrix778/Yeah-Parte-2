# Especificación de desarrollo — Portal Devilopers

Versión: 0.1 (MVP)
Stack: Django (monolito) + SQLite (dev) / PostgreSQL (prod) + templates HTML + Tailwind CSS + JavaScript vanilla
Proyecto Django: `DevilWeb` · Sitio público: **Devilopers**
Alcance: **núcleo únicamente**. Logros, webhooks y correos masivos quedan para v2.

---

## 1. Contexto

**Devilopers** es un equipo de desarrollo (videojuegos, sistemas, web) con una
identidad muy marcada: personajes dibujados a mano (Sanrix B, Elizabeth, Gurt,
Kike, Hat Guy, Rikix, Wachi), un tono informal y un aspecto de portal indie
"hecho a mano". Este sitio es su vitrina oficial: catálogo de juegos, personajes,
guías y el cómic de Sanrix.

La referencia visual (`Imagenes/Web.png`) es un portal tipo “comics + games” con
aspecto de mural dibujado: fondo gris oscuro, logo manuscrito gigante a la
izquierda, buscador redondeado al centro, menú y avatar a la derecha, una fila de
cuatro juegos y una fila de dos cómics debajo. **El diseño no es negociable**:
está detallado en `DESIGN.md` y su traducción a tokens está en §4 de este spec.

### 1.1 Bloques

| Bloque | Contenido | Estado MVP |
|---|---|---|
| **Inicio** | cards de juegos, cards de comics, “conócenos más” | ✅ |
| **Juegos** | de qué trata, por qué salió la idea, categoría, plataforma, personajes (FK), walkthrough, equipo, link externo | ✅ |
| **Personajes** | nombre, rol, descripción, retrato, color de ficha | ✅ |
| **Comics** | portadas, capítulos, lector de imágenes básico | ✅ |
| **Equipos / créditos** | participantes por juego con rol y alias público | ✅ |
| **Cuentas** | registro, login, perfil con avatar | ✅ |
| **Logros** | nombre, juego, descripción, token activador | ❌ v2 |
| **Correos masivos** | campañas | ❌ v2 |

### 1.2 Contenido inicial (semilla del MVP)

El sitio arranca con el contenido que ya existe en el repo:

**Juegos** (las 4 cards del mockup, en este orden):

| Título | Plataforma | Notas |
|---|---|---|
| Devil Hide Roblox | Roblox | juego principal |
| Devil Hide en Web | Web | versión navegador del mismo juego |
| Test Place | Roblox | zona de pruebas, sin fecha de salida |
| Cookie - Clicker | Web | juego corto tipo idle/clicker |

**Comics:**

| Capítulo | Portada |
|---|---|
| Sanrix #1 | `Imagenes/SanrixBlox_alt2.png` |
| Sanrix, Chapter 1 | `Imagenes/SanrixBlox.png` |

**Personajes** (derivados de `Imagenes/Iconos/`): Sanrix B, Elizabeth, Gurt, Kike,
Hat Guy, Rikix, Wachi.

### 1.3 Objetivos MVP

1. Publicar y gestionar el catálogo de juegos con su información completa.
2. Mostrar los personajes de cada juego con su identidad visual.
3. Publicar el cómic de Sanrix y poder leerlo desde el sitio.
4. Mostrar los créditos de cada juego agrupados por rol.
5. Permitir registro/login y edición de perfil (el avatar vive en el header).
6. Sitio público navegable sin login, responsive, sin build step complejo.

### 1.4 Fuera de alcance (v2)

- Logros y token activador con webhook de activación.
- Lector de comics avanzado (avance de lectura, capítulo siguiente automático).
- Módulo de correos masivos (campañas, plantillas, envío por lotes).
- API pública, app móvil, i18n, comentarios/social.

---

## 2. Stack y decisiones técnicas

### 2.1 Base

| Capa | Elección | Nota |
|---|---|---|
| Lenguaje | Python 3.9 | **Bloqueante:** la máquina solo tiene 3.9. Ver nota abajo. |
| Framework | Django 4.2 LTS | Trae admin, ORM, auth y templates. Monolito. |
| BD (dev) | **SQLite** | `db.sqlite3` en la raíz. Cero fricción para arrancar. |
| BD (prod) | PostgreSQL 16 | Solo cambia `DATABASES` vía `DATABASE_URL`. Docker en dev cuando haga falta. |
| ORM | Django ORM | Sin migraciones manuales |
| Frontend | Django Templates | Server-rendered, sin SPA |
| CSS | Tailwind CSS v4 vía `django-tailwind` | Un comando de build |
| JS | JavaScript vanilla (ES modules) | Sin bundler. Sin framework. |
| Auth | `django.contrib.auth` con `AbstractUser` custom | Sesiones + CSRF |
| Archivos | `ImageField` a disco en dev, `django-storages` (S3/MinIO) en prod | |
| Tests | `pytest-django` | |

**Desviación del stack (2026-10-09).** Este spec pedía Python 3.13 + Django
5.2 LTS. La máquina tiene **solo Python 3.9**, y Django 5.2 exige ≥ 3.10. Se
implementó con **Django 4.2 LTS**, que es lo que el proyecto ya usaba y lo que
soporta 3.9.

El código escrito es compatible con Django 5.2 (no usa APIs deprecadas), así que
subir de versión es solo esto:

```bash
# 1. Instalar Python 3.13 y recrear el venv
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest          # debería pasar igual
# 2. Cambiar el pin en pyproject.toml a "Django>=5.2,<5.3"
```

Nada del modelo de datos, las vistas ni las plantillas depende de 4.2.

**Sobre SQLite.** Es la base del MVP y no se migra ahora. Restricciones a tener
presentes para no diseñar sobre capacidades que no existen:

- Sin `JSONField` indexado ni `ArrayField` (no existen en SQLite). Los campos
  `JSONField` del MVP se usan solo para datos auxiliares, nunca filtrados.
- Sin `select_for_update()` transaccional efectivo. No depende ningún flujo del
  MVP de escrituras concurrentes.
- Los `.sqlite3` no se versionan en git y el seed se reconstruye con
  `python manage.py loaddata`.

La migración a PostgreSQL es un cambio de una línea en settings más un `dumpdata`
/`loaddata`. No requiere reescribir modelos.

**Regla de oro:** el servidor renderiza el HTML. JS solo mejora la experiencia
(tabs, confirmaciones, galería del lector, atajos de teclado). Si una
funcionalidad no necesita JS, no lleva JS.

### 2.2 Por qué monolito Django

El equipo es chico y heterogéneo (no todos backend). Un monolito con admin
gratis permite que alguien cargue juegos, personajes y capítulos sin escribir
código. La lógica es CRUD + un lector de imágenes; no justifica desacoplar.

### 2.3 Estructura de proyecto

```
Yeah-Parte-2/
├─ DESIGN.md                 # brief visual (fuente de verdad del estilo)
├─ docs/spec.md              # este documento
├─ manage.py → DevilWeb/manage.py
├─ pyproject.toml            # deps + config ruff/pytest
├─ .env.example
├─ docker-compose.yml        # postgres (solo cuando se migre)
├─ config/
│  ├─ settings/{base,dev,prod}.py
│  ├─ urls.py  wsgi.py  asgi.py
├─ apps/
│  ├─ accounts/      # User custom, perfil, registro, vistas de cuenta
│  ├─ games/         # Game, Category, Character, WalkthroughSection, Participant
│  ├─ comics/        # Comic, ComicChapter
│  └─ site/          # home, about, páginas públicas, búsqueda
├─ templates/
│  ├─ base.html
│  ├─ partials/      # header.html, search-bar.html, game-card.html, comic-card.html
│  └─ components/
├─ static/
│  ├─ css/{input.css,dist/output.css}
│  ├─ js/
│  └─ img/           # logos, portadas y decorados fijos (fuera del admin)
├─ media/            # subidas del admin (avatares, retratos, capítulos)
├─ Imagenes/         # material de trabajo actual → se migra a static/img y media/
└─ tests/
```

**Convención de assets.** Los archivos que edita el equipo (`Imagenes/`) se
mueven a `static/img/` (decorados: logo, fondos, thumbnails fijos). Los archivos
que sube un staff desde el admin van a `media/`. Nunca se sirven PNG sueltos
sueltos en la raíz del repo.

---

## 3. Modelo de datos

### 3.1 `accounts.User` (AUTH_USER_MODEL)

```python
class User(AbstractUser):
    email = models.EmailField(unique=True)          # login por email o username
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

`UserProfile` no se separa: los campos son 1:1 fijos y evita un JOIN extra. Si
más adelante crece (preferencias, notificaciones), se extrae a perfil.

**Login:** se permite con `username` **o** `email` (backend de auth custom, ~20
líneas).

### 3.2 `games.Category`

```python
class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=200, blank=True)
    accent_color = models.CharField(max_length=7, default="#6b7280")  # HEX
```

Catálogo cerrado y pequeño (Acción, Supervivencia, Terror, Puzzle, Clicker,
Herramienta, Web, Otro). Lo edita un staff desde el admin. Se cachea con
`cache.get_or_set("categories")`.

### 3.3 `games.Game`

```python
class GameStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    UPCOMING = "upcoming", "Próximamente"
    RELEASED = "released", "Publicado"
    ARCHIVED = "archived", "Archivado"

class Platform(models.TextChoices):
    ROBLOX = "roblox", "Roblox"
    WEB = "web", "Web"
    PC = "pc", "PC"
    MOBILE = "mobile", "Móvil"
    OTHER = "other", "Otro"

class Game(models.Model):
    title = models.CharField(max_length=140)
    slug = models.SlugField(unique=True)                       # auto desde title
    platform = models.CharField(max_length=16, choices=Platform, default=Platform.WEB)
    tagline = models.CharField(max_length=180, blank=True)     # 1 línea para la card
    about = models.TextField()                                 # "de qué trata"
    origin = models.TextField(blank=True)                      # "por qué salió la idea"
    category = models.ForeignKey(Category, on_delete=PROTECT, related_name="games")
    cover_image = models.ImageField(upload_to="games/covers/")
    thumbnail = models.ImageField(upload_to="games/thumbs/", blank=True)
                                      # recorte cuadrado de la card (aspect 1:1)
    accent_color = models.CharField(max_length=7, blank=True)   # color del borde/ficha
    external_url = models.URLField(blank=True)                 # itch.io / Roblox / store
    engine = models.CharField(max_length=40, blank=True)       # Roblox Studio, Godot, web…
    status = models.CharField(choices=GameStatus, default=DRAFT)
    released_at = models.DateField(null=True, blank=True)
    featured = models.BooleanField(default=False)              # aparece en la home
    order = models.PositiveSmallIntegerField(default=0)        # orden manual en la home

    # SEO / social
    meta_description = models.CharField(max_length=160, blank=True)

    created_at, updated_at
```

**Variantes de un mismo juego.** “Devil Hide Roblox” y “Devil Hide en Web” son
registros separados con `platform` distinta: cada uno tiene su link, su estado y
su thumb. Así la home puede mostrar cuatro cards distintas sin un modelo extra.
Si más adelante hace falta agruparlas (“ver todos los ports de X”), se agrega
`parent = ForeignKey("self", null=True)`. Decisión abierta §11.

**Visibilidad:** el listado público y las páginas solo exponen
`status != DRAFT`. El admin filtra por defecto.

### 3.4 `games.Character`

```python
class Character(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE, related_name="characters")
    name = models.CharField(max_length=100)        # "Sanrix B", "Elizabeth"
    slug = models.SlugField()
    role = models.CharField(max_length=60, blank=True)   # protagonista, rival, guía…
    description = models.TextField(blank=True)
    portrait = models.ImageField(upload_to="characters/", blank=True)
    color = models.CharField(max_length=7, default="#6b7280")  # color de ficha
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ("game", "slug")
        ordering = ("order", "name")
```

`Character` cuelga de un juego porque el mismo personaje puede aparecer en varios
(juego + cómic). Si aparece en ambos, se crean dos fichas con el mismo `name` y
`portrait` compartido visualmente.

### 3.5 `games.WalkthroughSection`

El walkthrough es una guía con secciones navegables, no un bloque de texto único.

```python
class WalkthroughSection(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE, related_name="walkthrough_sections")
    title = models.CharField(max_length=140)
    slug = models.SlugField()
    order = models.PositiveSmallIntegerField(default=0)
    is_public = models.BooleanField(default=False)   # guía en construcción
    content = models.TextField(blank=True)           # markdown renderizado server-side

    class Meta:
        unique_together = ("game", "slug")
        ordering = ("order", "title")
```

`content` se renderiza con un saneador (`markdown` + `nh3`). Nunca HTML crudo
del admin sin limpiar.

### 3.6 `games.Participant` (n:m User ↔ Game con rol)

```python
class TeamRole(models.TextChoices):
    LEAD = "lead", "Lead"
    CODE = "code", "Programación"
    ART = "art", "Arte"
    DESIGN = "design", "Diseño"
    AUDIO = "audio", "Audio"
    WRITING = "writing", "Escritura"
    QA = "qa", "QA"
    OTHER = "other", "Otro"

class Participant(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE, related_name="participants")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE,
                             related_name="participations", null=True)
    display_name = models.CharField(max_length=80)        # nombre público en créditos
    role = models.CharField(max_length=16, choices=TeamRole, default=TeamRole.OTHER)
    credit_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ("game", "display_name", "role")
```

`user` es **opcional a propósito**: alguien puede estar en los créditos sin tener
cuenta en el sitio. Cuando exista cuenta con el mismo alias, el admin la enlaza y
el perfil muestra sus participaciones.

### 3.7 `comics.Comic`

```python
class Comic(models.Model):
    title = models.CharField(max_length=140)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(max_length=180, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="comics/covers/")
    game = models.ForeignKey(Game, on_delete=SET_NULL, null=True, blank=True,
                             related_name="comics")      # crossover opcional
    is_published = models.BooleanField(default=False)
    created_at, updated_at
```

### 3.8 `comics.ComicChapter`

```python
class ComicChapter(models.Model):
    comic = models.ForeignKey(Comic, on_delete=CASCADE, related_name="chapters")
    number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=140, blank=True)   # "", "Chapter 1", "El inicio"
    slug = models.SlugField()
    pages = models.ManyToManyField("comics.ComicPage", related_name="chapters", blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("comic", "number")
        ordering = ("number",)


class ComicPage(models.Model):
    image = models.ImageField(upload_to="comics/pages/")
    alt_text = models.CharField(max_length=160, blank=True)   # accesibilidad
    order = models.PositiveSmallIntegerField(default=0)
```

`ComicPage` separado de `ComicChapter` permite reordenar y reusar páginas sin
tocar el capítulo, y que el lector itere sobre una queryset.

### 3.9 Diagrama de relaciones (resumen)

```
Category 1─* Game 1─* Character
                 1─* WalkthroughSection
                 1─* Participant *─1 User (opcional)
                 1─* Comic ─1─* ComicChapter *─* ComicPage
```

---

## 4. Identidad visual (traducción de `DESIGN.md`)

Esta sección es normativa. Si una decisión de `DESIGN.md` y esta discrepan, manda
el mockup `Imagenes/Web.png`, y manda esta sobre cualquier framework de estilos.

### 4.1 Tokens

Definidos en `static/css/input.css` con `@theme` de Tailwind v4:

```css
@theme {
  --color-devil-bg: #3d3d3d;        /* fondo general */
  --color-devil-panel: #1f1f1f;     /* bloque central, barras de sección */
  --color-devil-card: #0d0d0d;      /* fondo de card */
  --color-devil-ink: #f5f5f5;       /* texto principal */
  --color-devil-accent: #9e1717;    /* rojo de acento */
  --color-devil-accent-dark: #7a1010;
  --color-devil-line: #0a0a0a;      /* bordes y contornos */

  --font-hand: "Caveat", "Segoe Print", "Bradley Hand",
                "Comic Sans MS", "Marker Felt", cursive;
  --font-logo: "Caveat", cursive;    /* logo inclinado, más fuerte */
}
```

Reglas de uso:

- El fondo del `body` es `--color-devil-bg`, **sin degradado**.
- Los bloques de sección (la banda de “Games” y la de “Comics”) son
  `--color-devil-panel`, no cards.
- Las cards son `--color-devil-card` con `border: 2px solid --color-devil-line`.
- El `--color-devil-accent` solo se usa en detalles pequeños: badge de estado,
  borde activo de tab, icono de “nuevo”. Nunca como fondo grande.
- Bordes redondeados generosos (`rounded-3xl` en cards, `rounded-full` en la
  barra de búsqueda). Sombras suaves, sin glow ni degradado.

### 4.2 Layout del header

Grid de 3 columnas (`grid-cols-[auto_1fr_auto]`), contenido centrado con ancho
máximo de ~1200px:

| Zona | Contenido | Medidas |
|---|---|---|
| Izquierda | Logo **Devilopers** | `text-7xl` a `text-9xl`, `--font-logo`, inclinación -6° a -10°, transform-origin left |
| Centro | Barra de búsqueda | 420–500px, alto 64–72px, `rounded-full`, fondo blanco, lupa a la izquierda y micrófono a la derecha |
| Derecha | Menú (3 líneas) + avatar | 48px, avatar circular con borde oscuro |

El logo es **más grande que cualquier otro texto de la página** y se inclina
hacia la izquierda. No usar flexbox que lo estire: `width: max-content`.

### 4.3 Secciones de la home

```
[ header: Devilopers | buscador | menú+avatar ]
[          Games            ]   ← título centrado, banda panel, 4 cards
[ Comics  ]                   ← título a la izquierda, banda panel, 2 cards
```

- **Games**: 4 cards en una sola fila, ancho 200–240px, alto 240–260px,
  mismo tamaño, separación consistente. Miniatura cuadrada, título manuscrito
  grande debajo, a menos de 16px de la miniatura.
- **Comics**: 2 cards más grandes, alineadas a la izquierda bajo el título de
  sección. Miniatura con fondo claro/estilizado y título con aire de “logo de
  cómic” (mayúsculas, muy gruesa).

Ambos títulos de sección son manuscritos, grandes, con trazo irregular. “Games”
centrado; “Comics” pegado a la izquierda.

### 4.4 Assets de ilustración

Los thumbnails y las ilustraciones **no** son fotos ni renders 3D: son dibujos a
mano con contorno negro marcado, ojos rojos o muy saturados, fondos oscuros y
formas simples. Criterio al elegir un asset:

- Fondo transparente u oscuro uniforme, no degradado.
- El personaje ocupa el 60–80% del cuadro, centrado.
- Si es un retrato de ficha, fondo del `--color-devil-card` o el color del
  personaje.
- Cada card necesita `alt` descriptivo en español.

### 4.5 Responsive

- 1280–1440px: composición idéntica al mockup. Es el tamaño de referencia.
- 1024–1280px: las cards de juegos pasan a 3 por fila.
- < 768px: header en dos filas (logo, luego buscador + menú), 2 games por fila,
  2 comics por fila, tipografía del logo en `text-5xl`.
- Nunca scroll horizontal a 360px.

### 4.6 Anti-patrones

- ❌ Tarjetas con sombra larga, `box-shadow` coloreado o glow.
- ❌ Grids uniformes con esquinas vivas de 4px: el radio es grande siempre.
- ❌ Texto en Inter/Roboto/system-ui para títulos. Solo `--font-hand`.
- ❌ Interlineado justo y texto centrado en párrafos: el manual se deja crude.
- ❌ Iconos de paquete (Heroicons, FontAwesome) en el header. Los dos iconos del
  mockup son drawings; si no hay asset, se dibuja un SVG inline a mano.

---

## 5. Roles y permisos

| Rol | Puede |
|---|---|
| `Superuser` | todo |
| `Staff` | CRUD de juegos, personajes, walkthrough, cómics y capítulos en el admin |
| `Editor` | igual que staff, sin acceso a usuarios |
| `User` registrado | perfil, editar sus datos, ver en qué juegos participa |
| `Visitante` | solo lectura del contenido público |

Custom permissions: `games.can_manage_games`, `comics.can_manage_comics`.

La emisión/rotación de tokens (v2) queda restringida a `superuser`. Los tokens
son credenciales de escritura.

---

## 6. Mapa de URLs

Las URLs van en español; las etiquetas visibles copian el mockup (“Games”,
“Comics”).

```
/                                  site:home        (games + comics + CTA)
/buscar/                            site:search      ?q=  (resultados de juegos y comics)

/juegos/                           games:list       ?categoria=&plataforma=&estado=&q=
/juegos/<slug>/                    games:detail     tabs: Info │ Personajes │ Guía │ Equipo
/juegos/<slug>/guia/               games:walkthrough      índice de secciones
/juegos/<slug>/guia/<slug>/        games:walkthrough_detail
/categorias/<slug>/                games:category   listado filtrado

/comics/                           comics:list
/comics/<slug>/                    comics:detail    portada + lista de capítulos
/comics/<slug>/<slug>/             comics:reader    visor de páginas del capítulo

/cuentas/registro/                 accounts:signup
/cuentas/login/                    accounts:login   (email o username)
/cuentas/logout/                   accounts:logout  POST only
/cuentas/perfil/                   accounts:profile
/cuentas/password/                 accounts:password_change

/conocenos/                        site:about

/admin/                            admin del proyecto
/health/                           site:health      JSON, para deploy

# API JSON read-only ( groundwork para v2 )
/api/v1/games/                     games:api_list    GET
/api/v1/games/<slug>/              games:api_detail  GET
```

---

## 7. Vistas y templates

### 7.1 Home `/`

- Header (§4.2) con buscador que hace `GET /buscar/?q=`.
- Banda **Games** con 4 cards: portada cuadrada, título manuscrito, categoría y
  badge de estado (`Publicado` / `Próximamente`).
- Banda **Comics** con 2 cards: portada, número de capítulo y título.
- CTA “Conócenos más” al pie de la home.
- Los juegos salen ordenados por `order` y luego `featured`, no por fecha: el
  orden de la home es una decisión editorial, no cronológica.

### 7.2 Detalle de juego `/juegos/<slug>/`

Tabs en un solo HTML (JS solo cambia la visibilidad; la URL usa `?tab=`):

- **Info**: `about`, `origin` en un bloque citado (es parte de la identidad del
  equipo), metadata (categoría, plataforma, motor, `released_at`), link externo
  y botón “Jugar”.
- **Personajes**: grid de fichas con color y rol; vacío → mensaje elegante.
- **Guía**: índice de secciones; las `is_public=False` aparecen bloqueadas para
  staff.
- **Equipo**: participantes agrupados por rol.

### 7.3 Lector de comics `/comics/<slug>/<slug>/`

- Todas las páginas del capítulo en un scroll vertical,`<picture>` + `loading="lazy"`.
- Índice flotante de páginas (números) para saltar.
- Teclas `←` / `→` para página anterior/siguiente, `Esc` para volver.
- Sin progreso guardado (eso es v2).

### 7.4 Estándares visuales

- Tailwind con los tokens de §4.1. Nada de colores hex sueltos en templates.
- Cards con `aspect-square` para que la grilla no baile al cargar.
- Máximo 4 cards por fila en desktop, 1 en móvil.
- `<meta name="description">` desde `meta_description`.
- Open Graph para compartir.

### 7.5 JavaScript (vanilla, módulos en `static/js/`)

```
static/js/
├─ tabs.js            # tabs de página de juego, ~30 líneas
├─ search.js          # envío del buscador + estado del input
├─ reader.js          # navegación por teclado del lector de comics
├─ confirm.js         # confirmaciones en formularios destructivos
└─ theme.js           # toggle de tema (si se decide después)
```

Presupuesto: < 20 KB de JS total sin comprimir. Sin bundler, sin `node_modules`
en runtime.

---

## 8. Seguridad

| Riesgo | Mitigación |
|---|---|
| XSS en walkthrough | Render server-side con `markdown` + `nh3`, nunca `\|safe` sobre input de usuario |
| XSS en alt_text de páginas | Sale por el filtro de templates con `escape`, nunca `mark_safe` |
| CSRF | Middleware de Django en todas las vistas; `logout` solo por POST |
| Enumeración de usuarios | Mismo mensaje de error en login con email o username |
| Subida de archivos maliciosos | `ImageField` con Pillow, validadores de tipo y tamaño, nombres UUID |
| Fuerza bruta en login | `django-axes` o rate limit por IP en `/cuentas/login/` |
| Secrets en el repo | `SECRET_KEY` y `DEBUG` salen del código a `.env`; el valor hardcodeado actual se borra |
| Staff con permisos de más | Permisos custom, staff ≠ superuser |
| Deprecaciones | `pip-audit` + Dependabot en CI |

**Nota:** `DevilWeb/core/settings.py` hoy tiene `SECRET_KEY` y `DEBUG = True`
en el código. Es el primer cambio a hacer al arrancar el MVP (§13, paso 1).

---

## 9. Testing

```
tests/
├─ conftest.py               # factories (factory_boy): user, game, character
├─ test_games_views.py       # visibilidad, filtros, slug, 404 en draft
├─ test_walkthrough.py       # XSS: contenido malicioso no se ejecuta
├─ test_comics.py            # listado, capítulo, páginas en orden
├─ test_accounts.py          # registro, login con email, perfil
└─ test_home.py              # la home lista solo publicados, orden por `order`
```

Comandos: `pytest`, `pytest --cov=apps --cov-report=term-missing`, `ruff check .`,
`ruff format .`.

**Objetivo MVP:** ≥ 70% global, ≥ 85% en `games` y `comics`.

---

## 10. Entorno local

Todo se corre **desde la raíz del repo** (`Yeah-Parte-2/`), que es donde está
`manage.py`. El proyecto Django es `config/` y las apps viven en `apps/`.

```bash
git clone <repo> && cd Yeah-Parte-2
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"

python manage.py migrate
python manage.py createsuperuser
python manage.py setup_seed_assets              # copia Imagenes/ -> media/
python manage.py seed_content                   # categorías + 4 juegos + cómics

# dos terminales:
python manage.py runserver
python manage.py tailwind                      # build de CSS en watch mode
```

`pyproject.toml` trae la config de `pytest` (usa `config.settings.dev`).

`.env.example`:

```
DEBUG=1
SECRET_KEY=changeme
# DATABASE_URL=postgres://devilopers:devilopers@localhost:5432/devilweb   # prod
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
TAILWIND_APP=apps.site
```

**Seed.** `fixtures/seed_content.json` carga el contenido de §1.2. Los archivos
**Seed.** Dos comandos, en este orden:

1. `setup_seed_assets` copia los binarios de `Imagenes/` a `media/`
   (portadas de Sanrix + un placeholder para los juegos sin arte todavía).
2. `seed_content` crea las categorías, los 4 juegos y los 2 cómics.

Los juegos y cómics se crean con `update_or_create`, así que se puede correr
varias veces sin duplicar. Las **páginas de los capítulos** se cargan desde el
admin: son imágenes que el equipo tiene que subir.

CI (GitHub Actions): `ruff` → `pytest` → `migrate` → `collectstatic --dry-run`.
Deploy: Railway / Fly.io / VPS con `gunicorn config.wsgi` + whitenoise.

---

## 11. Backlog y preguntas abiertas

### 11.1 Preguntas a decidir antes de codear

1. **Agrupar ports.** ¿“Devil Hide Roblox” y “Devil Hide en Web” son dos juegos o
   uno con dos versiones? *Recomendación: dos registros con `platform` distinta
   (más simple); agregar `parent` si aparecen más ports.*
2. **Personajes compartidos.** Sanrix aparece en el juego y en el cómic. ¿Ficha
   duplicada por juego o un modelo `Character` global con ManyToMany a juegos?
   *Recomendación: ficha por juego en el MVP, global si aparecen muchos.*
3. **Idioma de las cards.** El mockup mezcla español e inglés (“Devil Hide”,
   “Test Place”, “Cookie - Clicker”, “SAN RIX”). ¿Los títulos quedan como están
   o se traducen? *Recomendación: los nombres propios quedan tal cual; los
   títulos de sección sí van en español si se decide cambiar el branding.*
4. **Búsqueda.** ¿Busca también en personajes y capítulos, o solo juegos y
   cómics? *Recomendación: juegos + cómics en el MVP.*
5. **Tema claro/oscuro.** El diseño es oscuro por naturaleza. ¿Hay modo claro o
   se elimina el toggle? *Recomendación: solo oscuro, sin toggle.*
6. **Registro abierto.** ¿Cualquiera se registra, o el registro es por invitación
   para que los créditos no se llenen de spam? *Recomendación: abierto, con
   moderación de alias en los créditos.*

### 11.2 v2 — logros y webhooks

`Achievement` (game, name, slug, description, icon, points, is_secret) →
`UserAchievement` (user, achievement, unlocked_at, progress, source,
`unique_together` para idempotencia) → `ActivatorToken` (hash SHA-256 del token,
mostrado una sola vez, `require_signature`, rate limit) → `WebhookLog`.

Endpoint `POST /api/v1/hooks/<token>/` con firma HMAC opcional. Los 92 iconos de
`Imagenes/Iconos/` (“Aim mode”, “Shoot Elizabeth”, “Rage Sanrix B”, “Curas”…)
sirven como `Achievement.icon` o como habilidades visibles de cada personaje.

### 11.3 v2 — lector avanzado

`ReadingProgress` (user, chapter, last_page, completed_at). Vista de “sigue
leyendo” en la home, capítulo siguiente automático, modo lectura sin scroll.

### 11.4 v2 — correos masivos

`Campaign` (name, subject, body_markdown, audience filter, status,
scheduled_at) → `CampaignRecipient` (campaign, user, sent_at, opened_at). Envío
por management command con `--batch-size`, sin Celery.

### 11.5 Ideas posteriores

- RSS de juegos y noticias.
- Changelog por juego.
- Estadísticas: juegos más vistos, personajes más buscados.
- Sponsors / créditos en el pie.

---

## 12. Historias de usuario (MVP)

| # | Historia | Criterio de aceptación |
|---|---|---|
| HU-01 | Como visitante, quiero ver la home con los juegos del equipo | La home lista solo juegos no-draft, 4 cards en una fila en desktop, orden editorial |
| HU-02 | Como visitante, quiero ver los comics en la home | 2 cards con portada y número de capítulo |
| HU-03 | Como visitante, quiero buscar un juego o comic por nombre | El buscador es un GET a `/buscar/`, funciona sin JS, resultados por tipo |
| HU-04 | Como visitante, quiero filtrar juegos por categoría y plataforma | Filtros por querystring, compartibles, funcionan sin JS |
| HU-05 | Como visitante, quiero leer de qué trata un juego y por qué salió la idea | Ambos textos en `/juegos/<slug>/`, con `origin` destacado |
| HU-06 | Como visitante, quiero ver los personajes de un juego | Grid de fichas con color; vacío → mensaje elegante, no error |
| HU-07 | Como visitante, quiero consultar la guía de un juego | Índice navegable; secciones privadas ocultas al público |
| HU-08 | Como visitante, quiero ver quién hizo cada juego | Créditos agrupados por rol, con nombre público |
| HU-09 | Como visitante, quiero registrarme | Email + contraseña, email único, auto-login |
| HU-10 | Como visitante, quiero entrar con email o username | Ambos funcionan, mismo mensaje de error para ambos |
| HU-11 | Como usuario, quiero editar mi perfil y avatar | Avatar validado (tipo + tamaño), bio de 500 chars máx. |
| HU-12 | Como visitante, quiero ver la lista de cómics y abrir un capítulo | Portada + capítulos en orden; capítulo vacío → mensaje, no 500 |
| HU-13 | Como visitante, quiero leer un capítulo cómodo | Imágenes con lazy loading y navegación por teclado |
| HU-14 | Como staff, quiero crear un juego completo desde el admin | Todos los campos de §3.3, sin tocar código |
| HU-15 | Como staff, quiero crear un capítulo con sus páginas | Las páginas se ordenan y el lector las respeta |
| HU-16 | Como visitante, quiero una página "conócenos más" | Historia del equipo, links, contacto |
| HU-17 | Como visitante, quiero que la home se vea igual al mockup | Cumple §4 en 1280–1440px |
| HU-18 | Como visitante, quiero navegar bien desde el móvil | Todo usable a 360px, sin scroll horizontal |

---

## 13. Orden de trabajo sugerido

1. **Andamiaje**: mover `SECRET_KEY`/`DEBUG` a `.env`, `pyproject`, settings
   base/dev/prod, estructura `apps/` + `config/`, Tailwind, `base.html` con los
   tokens de §4.1.
2. **Design system**: `partials/header.html` (logo, buscador, menú, avatar) y las
   dos cards (`game-card.html`, `comic-card.html`). Validar contra el mockup antes
   de seguir. (HU-17)
3. **games**: modelos + admin + vista de detalle con tabs. (HU-05..08, HU-14)
4. **comics**: modelos + admin + home + lector. (HU-12, HU-13, HU-15)
5. **accounts**: User custom, registro/login, perfil. (HU-09..11)
6. **site**: home completa, `/buscar/`, `/conocenos/`. (HU-01..04, HU-16)
7. **Seed**: migrar `Imagenes/` a `static/img` + `media/seed`, comando
   `seed_assets` y fixture con el contenido de §1.2.
8. **QA**: responsive, tests, `ruff`, primer deploy.

El paso 2 va primero a propósito: si el header y las cards no se parecen al
mockup, todo lo demás se construye sobre una base visual equivocada y hay que
rehacerlo.
