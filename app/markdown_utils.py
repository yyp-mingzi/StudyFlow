import markdown
import nh3
from markupsafe import Markup


ALLOWED_TAGS = {
    "a",
    "blockquote",
    "br",
    "code",
    "del",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "li",
    "ol",
    "p",
    "pre",
    "s",
    "strong",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "ul",
}
ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "code": {"class"},
    "pre": {"class"},
    "td": {"align"},
    "th": {"align"},
}
ALLOWED_URL_SCHEMES = {"http", "https", "mailto"}


def render_markdown(content_markdown: str) -> Markup:
    """Render Markdown, sanitize its HTML, then mark only the cleaned result safe."""
    rendered_html = markdown.markdown(
        content_markdown,
        extensions=["fenced_code", "tables"],
    )
    cleaned_html = nh3.clean(
        rendered_html,
        tags=ALLOWED_TAGS,
        clean_content_tags={"script", "style", "iframe", "object", "embed"},
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=ALLOWED_URL_SCHEMES,
    )
    return Markup(cleaned_html)
