"""HTML renderer using Jinja2 template — sections-aware."""

import os
import re
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def render(sections: list[dict], date_str: str) -> str:
    """Render section-structured curated articles to HTML.

    *sections* is a list of dicts, each with keys:
        id, name, color, icon, articles (list of article dicts)
    """
    env = Environment(loader=FileSystemLoader(_TEMPLATE_DIR))

    # Filter: strip HTML tags from summary text
    def strip_html(text: str) -> str:
        if not text:
            return ""
        # Remove img tags (including malformed ones without closing >)
        text = re.sub(r'<img\b[^>]*(?:>|\s*/?)', '', text)
        # Remove <a> tags and their content (including malformed ones)
        text = re.sub(r'<a\b[^>]*(?:>|\s*/?)', '', text)
        # Remove </a> closing tags
        text = re.sub(r'</a>', '', text)
        # Remove any remaining html tags (including malformed)
        text = re.sub(r'<[^>]*(?:>|$)', '', text)
        # Decode URL-encoded chars &#x2F; -> / etc.
        text = re.sub(r'&#x2F;', '/', text, flags=re.IGNORECASE)
        text = re.sub(r'&#47;', '/', text, flags=re.IGNORECASE)
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    env.filters['strip_html'] = strip_html

    template = env.get_template("index.html")

    # Pre-strip HTML from all article summaries before rendering
    for sec in sections:
        for art in sec.get("articles", []):
            if art.get("summary"):
                art["summary"] = strip_html(art["summary"])

    # Count total articles across all sections
    total_articles = sum(len(s.get("articles", [])) for s in sections)

    html = template.render(
        date=date_str,
        sections=sections,
        total_articles=total_articles,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S CST"),
    )

    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(_OUTPUT_DIR, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[Render] HTML written to {output_path} ({total_articles} articles in {len(sections)} sections)")
    return output_path
