"""Hacker News crawler via Firebase API."""

import httpx
from src.config import AI_KEYWORDS, TARGET_COMPANIES

HN_TOP_STORIES = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"


def fetch() -> list[dict]:
    """Fetch AI-related top stories from Hacker News."""
    articles: list[dict] = []
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(HN_TOP_STORIES)
            resp.raise_for_status()
            story_ids = resp.json()[:100]

            for sid in story_ids[:60]:
                try:
                    item = client.get(HN_ITEM.format(sid)).json()
                    title = (item.get("title") or "").lower()
                    text = (item.get("text") or "").lower()
                    combined = title + " " + text

                    hit = any(kw.lower() in combined for kw in AI_KEYWORDS)
                    hit |= any(c.lower() in combined for c in TARGET_COMPANIES)
                    if not hit:
                        continue

                    url = item.get("url") or f"https://news.ycombinator.com/item?id={sid}"
                    articles.append({
                        "title": item.get("title", "Untitled"),
                        "url": url,
                        "score": item.get("score", 0),
                        "source": "Hacker News",
                        "description": (item.get("text") or "")[:300],
                    })
                except Exception:
                    continue
    except Exception as e:
        print(f"[HackerNews] Error: {e}")
    print(f"[HackerNews] Fetched {len(articles)} articles")
    return articles
