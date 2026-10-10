"""Template tags de apps.site."""
import markdown
import nh3
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# El contenido de la guía lo escribe un staff en el admin, pero se sanea igual:
# el admin es un ser humano y los navegadores también ejecutan cosas rarezas
# (spec §8: "XSS en walkthrough").
ALLOWED_TAGS = {
    "p", "br", "hr",
    "strong", "em", "u", "s", "sub", "sup",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "blockquote", "pre", "code",
    "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
}
ALLOWED_ATTRS = {
    # nh3 gestiona `rel` de los links por su cuenta (link_rel), por eso no se
    # permite como atributo libre: declararlo acá hace lanzar ValueError.
    "a": {"href", "title"},
    "img": {"src", "alt", "title", "width", "height", "loading"},
}


@register.filter(name="markdownify")
def markdownify(value):
    """Renderiza Markdown a HTML seguro (markdown -> nh3).

    Es el único punto donde se devuelve HTML sanitizado; el resultado es
    marcado seguro por diseño porque nh3 elimina todo lo no permitido.
    """
    if not value:
        return ""
    html = markdown.markdown(
        value,
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html",
    )
    safe = nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        url_schemes={"http", "https", "mailto"},
    )
    return mark_safe(safe)