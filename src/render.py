"""HTML renderer using Jinja2 template."""

import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def render(articles: list[dict], date_str: str) -> str:
    """Render curated articles to HTML and return the output path."""
    env = Environment(loader=FileSystemLoader(_TEMPLATE_DIR))
    template = env.get_template("index.html")

    html = template.render(
        date=date_str,
        articles=articles,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S CST"),
    )

    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(_OUTPUT_DIR, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[Render] HTML written to {output_path}")
    return output_path
