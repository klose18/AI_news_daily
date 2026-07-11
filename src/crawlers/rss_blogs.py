"""RSS feed crawler for AI company blogs."""

import feedparser
from src.config import RSS_FEEDS


def fetch() -> list[dict]:
    """Fetch latest posts from AI company blogs via RSS."""
    articles: list[dict] = []
    for feed_url, source_name in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                articles.append({
                    "title": entry.get("title", "Untitled"),
                    "url": entry.get("link", ""),
                    "source": source_name,
                    "description": (entry.get("summary", "") or "")[:300],
                    "score": 0,
                })
        except Exception as e:
            print(f"[RSS {source_name}] Error: {e}")
    print(f"[RSS Blogs] Fetched {len(articles)} articles")
    return articles
