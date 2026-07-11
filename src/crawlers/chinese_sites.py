"""Chinese AI news site crawlers."""

import feedparser
import httpx
from bs4 import BeautifulSoup


def fetch() -> list[dict]:
    """Fetch articles from Chinese AI news sources."""
    articles: list[dict] = []
    articles.extend(_fetch_jiqizhixin())
    articles.extend(_fetch_qbitai())
    articles.extend(_fetch_36kr())
    articles.extend(_fetch_agihunt())
    print(f"[Chinese Sites] Fetched {len(articles)} articles")
    return articles


def _fetch_jiqizhixin() -> list[dict]:
    articles: list[dict] = []
    try:
        feed = feedparser.parse("https://www.jiqizhixin.com/rss")
        for entry in feed.entries[:15]:
            articles.append({
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", ""),
                "source": "机器之心",
                "description": (entry.get("summary", "") or "")[:300],
                "score": 0,
            })
    except Exception as e:
        print(f"[机器之心] Error: {e}")
    return articles


def _fetch_qbitai() -> list[dict]:
    articles: list[dict] = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
        }
        with httpx.Client(timeout=15, headers=headers) as client:
            resp = client.get("https://www.qbitai.com")
            soup = BeautifulSoup(resp.text, "html.parser")
            for item in soup.select("a[href*='/article/']")[:15]:
                title = item.get_text(strip=True)
                href = item.get("href", "")
                if not title or len(title) < 5:
                    continue
                url = href if href.startswith("http") else f"https://www.qbitai.com{href}"
                articles.append({
                    "title": title,
                    "url": url,
                    "source": "量子位",
                    "description": "",
                    "score": 0,
                })
    except Exception as e:
        print(f"[量子位] Error: {e}")
    return articles


def _fetch_36kr() -> list[dict]:
    articles: list[dict] = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
        }
        with httpx.Client(timeout=15, headers=headers) as client:
            resp = client.get("https://36kr.com/information/AI/")
            soup = BeautifulSoup(resp.text, "html.parser")
            for item in soup.select("a[href*='/p/']")[:15]:
                title = item.get_text(strip=True)
                href = item.get("href", "")
                if not title or len(title) < 5:
                    continue
                url = href if href.startswith("http") else f"https://36kr.com{href}"
                articles.append({
                    "title": title,
                    "url": url,
                    "source": "36氪",
                    "description": "",
                    "score": 0,
                })
    except Exception as e:
        print(f"[36氪] Error: {e}")
    return articles


def _fetch_agihunt() -> list[dict]:
    articles: list[dict] = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
        }
        with httpx.Client(timeout=15, headers=headers) as client:
            resp = client.get("https://www.agihunt.ai")
            soup = BeautifulSoup(resp.text, "html.parser")
            for item in soup.select("a[href]")[:20]:
                title = item.get_text(strip=True)
                href = item.get("href", "")
                if not title or len(title) < 8:
                    continue
                url = href if href.startswith("http") else f"https://www.agihunt.ai{href}"
                articles.append({
                    "title": title,
                    "url": url,
                    "source": "AGI Hunt",
                    "description": "",
                    "score": 0,
                })
    except Exception as e:
        print(f"[AGI Hunt] Error: {e}")
    return articles
