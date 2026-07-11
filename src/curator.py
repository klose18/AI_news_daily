"""AI curation and summarization via DeepSeek API."""

import json
import os

from openai import OpenAI
from src.config import DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, TARGET_COMPANIES


def curate(articles: list[dict], date_str: str) -> list[dict]:
    """Use DeepSeek to select top 10 articles and generate summaries."""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("[Curator] DEEPSEEK_API_KEY not set, using fallback")
        return _fallback(articles)

    if len(articles) <= 10:
        return _quick_summarize(articles, api_key)

    # Build prompt
    articles_text = ""
    for i, art in enumerate(articles):
        desc = (art.get("description", "") or "")[:200].replace("\n", " ")
        articles_text += f"[{i}] 标题: {art['title']}\n"
        articles_text += f"    来源: {art['source']}\n"
        articles_text += f"    链接: {art['url']}\n"
        if desc:
            articles_text += f"    简介: {desc}\n"
        articles_text += "\n"

    companies_str = ", ".join(TARGET_COMPANIES)
    prompt = (
        f"今天是 {date_str}。以下是今天从各个来源收集到的AI行业相关资讯。\n\n"
        f"请从中筛选出10条最重要的资讯，优先选择与大厂相关的重大消息。\n"
        f"重点关注的大厂：{companies_str}\n\n"
        "要求：\n"
        "1. 选出最重要的10条\n"
        "2. 为每条撰写2-3句中文摘要，概括核心内容\n"
        "3. 标题保持原文语言\n"
        "4. 必须包含原文链接和来源\n"
        "5. 严格按JSON数组格式输出，不要输出其他内容\n\n"
        "输出格式：\n"
        '[{"title": "标题", "summary": "2-3句中文摘要", "url": "原文链接", "source": "来源名称"}, ...]\n\n'
        f"以下是所有资讯：\n\n{articles_text}"
    )

    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的AI行业资讯编辑。请严格按JSON格式输出筛选结果，不要输出任何其他文字。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        result_text = response.choices[0].message.content or ""
        curated = _parse_json(result_text)
        if curated:
            print(f"[Curator] DeepSeek selected {len(curated)} articles")
            return curated[:10]
    except Exception as e:
        print(f"[Curator] DeepSeek error: {e}")

    return _fallback(articles)


def _quick_summarize(articles: list[dict], api_key: str) -> list[dict]:
    """Summarize when there are 10 or fewer articles."""
    titles = "\n".join(f"- {a['title']} | {a['source']}" for a in articles)
    prompt = (
        f"为以下AI资讯撰写摘要。\n\n{titles}\n\n"
        "为每条资讯撰写2-3句中文摘要。输出JSON数组：\n"
        '[{"title": "原标题", "summary": "摘要", "url": "链接", "source": "来源"}, ...]'
    )
    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "你是AI行业编辑，严格按JSON格式输出。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        result_text = response.choices[0].message.content or ""
        curated = _parse_json(result_text)
        if curated:
            return curated
    except Exception as e:
        print(f"[Curator] Quick summarize error: {e}")
    return _fallback(articles)


def _parse_json(text: str) -> list[dict] | None:
    """Extract and parse JSON array from LLM response."""
    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except (json.JSONDecodeError, Exception) as e:
        print(f"[Curator] JSON parse error: {e}")
        print(f"[Curator] Raw response: {text[:500]}")
    return None


def _fallback(articles: list[dict]) -> list[dict]:
    """Fallback: return top-scored articles without AI summary."""
    articles = sorted(articles, key=lambda x: x.get("score", 0), reverse=True)
    seen: set[str] = set()
    result: list[dict] = []
    for a in articles:
        if a["url"] in seen:
            continue
        seen.add(a["url"])
        result.append({
            "title": a["title"],
            "summary": (a.get("description") or "暂无摘要")[:200],
            "url": a["url"],
            "source": a["source"],
        })
        if len(result) >= 10:
            break
    print(f"[Curator] Fallback: {len(result)} articles")
    return result
