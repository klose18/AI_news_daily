#!/usr/bin/env python3
"""AI News Daily — main orchestrator (v2, sections-aware).

Usage:
    DEEPSEEK_API_KEY=sk-xxx python main.py
"""

import sys
from datetime import datetime

from src.crawlers import hackernews, community, rss_blogs, chinese_sites
from src.curator import curate
from src.render import render


def deduplicate(articles: list[dict]) -> list[dict]:
    """Remove duplicate articles by URL."""
    seen: set[str] = set()
    result: list[dict] = []
    for a in articles:
        url = a.get("url", "")
        if url and url not in seen:
            seen.add(url)
            result.append(a)
    return result


def main() -> None:
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"=== AI News Daily v2 — {date_str} ===\n")

    # Phase 1: Collect from all sources
    print("[Main] Starting crawlers...")
    all_articles: list[dict] = []
    all_articles.extend(hackernews.fetch())
    all_articles.extend(community.fetch())
    all_articles.extend(rss_blogs.fetch())
    all_articles.extend(chinese_sites.fetch())

    print(f"\n[Main] Total raw articles: {len(all_articles)}")

    # Deduplicate
    all_articles = deduplicate(all_articles)
    print(f"[Main] After dedup: {len(all_articles)}")

    if not all_articles:
        print("[Main] No articles collected, generating empty page.")
        render([], date_str)
        return

    # Phase 2: AI curation → sections
    print("\n[Main] Calling DeepSeek for classification + summary...")
    sections = curate(all_articles, date_str)

    total = sum(len(s.get("articles", [])) for s in sections)
    for s in sections:
        count = len(s.get("articles", []))
        if count:
            print(f"  [{s['name']}] {count} articles")
    print(f"[Main] Total curated: {total} articles across {len(sections)} sections")

    # Phase 3: Render HTML
    output_path = render(sections, date_str)

    print(f"\n=== Done: {output_path} ===")
    sys.exit(0)


if __name__ == "__main__":
    main()
