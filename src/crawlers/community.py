"""Community & aggregator sources: Techmeme, Ars Technica, Hugging Face."""

import feedparser
import httpx
from src.config import COMMUNITY_FEEDS


def fetch() -> list[dict]:
    """Fetch AI articles from community sources and aggregators."""
    articles: list[dict] = []

    # RSS-based sources
    for feed_url, source_name in COMMUNITY_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:15]:
                title = (entry.get("title") or "").lower()
                desc = (entry.get("summary", "") or "").lower()
                combined = title + " " + desc
                # Techmeme and Ars Technica cover broad tech - filter for AI
                if not _is_ai_related(combined):
                    continue
                articles.append({
                    "title": entry.get("title", "Untitled"),
                    "url": entry.get("link", ""),
                    "source": source_name,
                    "description": (entry.get("summary", "") or "")[:300],
                    "score": 0,
                })
        except Exception as e:
            print(f"[{source_name}] Error: {e}")

    # Hugging Face Daily Papers API
    articles.extend(_fetch_huggingface())

    print(f"[Community] Fetched {len(articles)} articles")
    return articles


def _fetch_huggingface() -> list[dict]:
    """Fetch from Hugging Face daily papers API."""
    articles: list[dict] = []
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get("https://huggingface.co/api/daily_papers")
            resp.raise_for_status()
            papers = resp.json()
            for paper in papers[:10]:
                title = paper.get("title", "")
                paper_id = paper.get("paper", {}).get("id", "")
                url = f"https://huggingface.co/papers/{paper_id}" if paper_id else ""
                articles.append({
                    "title": title,
                    "url": url,
                    "source": "Hugging Face Papers",
                    "description": (paper.get("paper", {}).get("summary", "") or "")[:300],
                    "score": paper.get("upvotes", 0),
                })
    except Exception as e:
        print(f"[HuggingFace] Error: {e}")
    return articles


def _is_ai_related(text: str) -> bool:
    """Check if text is AI-related."""
    keywords = [
        "ai", "artificial intelligence", "llm", "gpt", "claude", "gemini",
        "openai", "anthropic", "deepmind", "meta ai", "nvidia",
        "machine learning", "deep learning", "transformer", "diffusion",
        "neural network", "chatgpt", "copilot", "grok", "mistral",
    ]
    return any(kw in text for kw in keywords)
