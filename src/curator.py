"""AI curation via DeepSeek: classify, summarize, split into sections."""

import json
import os

from openai import OpenAI
from src.config import (
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    CATEGORY_VALUES,
    SECTIONS,
    SOURCE_CATEGORY_MAP,
    TARGET_TOTAL,
    MIN_PER_SECTION,
    MAX_PER_SECTION,
    TARGET_COMPANIES,
)


def curate(articles: list[dict], date_str: str) -> list[dict]:
    """Classify and summarize articles into sections.

    Returns a list of section dicts matching SECTIONS structure,
    each with a filled ``articles`` list.
    """
    # ── Step 1: try DeepSeek ──────────────────────────────────────
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if api_key:
        classified = _deepseek_classify(articles, date_str, api_key)
        if classified:
            return _build_sections(classified)

    # ── Step 2: fallback ──────────────────────────────────────────
    print("[Curator] Fallback: source-based categorisation")
    articles = sorted(articles, key=lambda x: x.get("score", 0), reverse=True)
    classified = _fallback_classify(articles)
    return _build_sections(classified, force_flat=len(articles) < 5)


# ── DeepSeek-powered classification ───────────────────────────────

def _deepseek_classify(
    articles: list[dict], date_str: str, api_key: str
) -> list[dict] | None:
    """Ask DeepSeek to classify & summarise all articles, return augmented list."""

    articles_text = ""
    for i, art in enumerate(articles):
        desc = (art.get("description") or "")[:200].replace("\n", " ")
        articles_text += f"[{i}] 标题: {art['title']}\n"
        articles_text += f"    来源: {art['source']}\n"
        articles_text += f"    链接: {art['url']}\n"
        if desc:
            articles_text += f"    简介: {desc}\n"
        articles_text += "\n"

    companies_str = ", ".join(TARGET_COMPANIES)

    prompt = (
        f"今天是 {date_str}。以下是AI行业相关资讯列表。\n\n"
        f"请为每篇资讯做两件事：\n"
        "1. **分类**：将其归入以下五个板块之一\n"
        "2. **摘要**：用 2-3 句中文概括核心内容\n\n"
        "板块定义：\n"
        "- headline（要闻）：AI大厂及其核心高管的重大动态——战略发布、合作、融资、人事变动、CEO公开发言等\n"
        "- dev_eco（开发生态）：各AI公司的开发者相关更新——API变动、SDK更新、定价调整、平台政策、开源工具\n"
        "- model_launch（模型发布）：新模型的推出或升级——文本模型、coding模型、多模态模型、视频生成模型\n"
        "- product_app（产品应用）：AI产品的具体应用案例、新产品上线、产品功能更新、AI硬件\n"
        "- industry（行业动态）：行业趋势、监管政策、学术突破、融资并购、人才流动、竞合关系\n\n"
        f"重点关注的大厂：{companies_str}\n\n"
        "要求：\n"
        "1. 每篇文章都必须输出 category + title + summary + url + source\n"
        "2. 选出的总数控制在 15 条左右，每个板块最多 5 条\n"
        "3. 优先保留重要大厂相关资讯\n"
        "4. 严格按 JSON 数组格式输出，不要输出其他文字\n\n"
        "输出格式：\n"
        '[{"title": "标题", "category": "headline", "summary": "2-3句中文摘要", "url": "原文链接", "source": "来源名称"}, ...]\n\n'
        f"以下是所有资讯：\n\n{articles_text}"
    )

    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一个专业的AI行业资讯编辑。"
                        "请严格按JSON格式输出分类和摘要结果，不要输出任何其他文字。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=8192,
        )
        result_text = response.choices[0].message.content or ""
        curated = _parse_json(result_text)
        if curated:
            print(f"[Curator] DeepSeek returned {len(curated)} classified articles")
            return curated
    except Exception as e:
        print(f"[Curator] DeepSeek error: {e}")

    return None


# ── Fallback classification (source-based) ─────────────────────────

def _fallback_classify(articles: list[dict]) -> list[dict]:
    """Classify articles by source when DeepSeek is unavailable."""
    result: list[dict] = []
    seen: set[str] = set()
    for art in articles:
        url = art.get("url", "")
        if not url or url in seen:
            continue
        seen.add(url)
        source = art.get("source", "")
        cats = SOURCE_CATEGORY_MAP.get(source, ("industry",))
        result.append({
            "title": art["title"],
            "url": url,
            "source": source,
            "summary": (art.get("description") or "暂无摘要")[:200],
            "category": cats[0],
        })
    return result


# ── Build sections structure ──────────────────────────────────────

def _build_sections(
    classified: list[dict],
    force_flat: bool = False,
) -> list[dict]:
    """Distribute classified articles into section buckets.

    When *force_flat* is True (fewer than 5 total articles) all
    articles go into a single virtual section.
    """
    if not classified:
        return _empty_sections()

    if force_flat:
        # Show everything, limit 15
        bucket: dict[str, list] = {}
        for art in classified[:TARGET_TOTAL]:
            cat = art.get("category", "industry")
            bucket.setdefault(cat, []).append(art)
        return _merge_sections(bucket)

    # Normal: one bucket per category, respect per-section limits
    bucket: dict[str, list] = {}
    for art in classified:
        cat = art.get("category", "industry")
        if cat not in CATEGORY_VALUES:
            cat = "industry"
        bucket.setdefault(cat, []).append(art)

    # Enforce per-section caps
    total = 0
    for cat in CATEGORY_VALUES:
        bucket[cat] = bucket.get(cat, [])[:MAX_PER_SECTION]
        total += len(bucket[cat])

    # If we have more than TARGET_TOTAL, trim the least important sections
    # (prefer keeping headline, model_launch)
    if total > TARGET_TOTAL:
        trim_order = ("product_app", "industry", "dev_eco", "model_launch", "headline")
        for cat in trim_order:
            while len(bucket.get(cat, [])) > MIN_PER_SECTION and total > TARGET_TOTAL:
                bucket[cat].pop()
                total -= 1

    # If a section is empty, leave it empty (template will skip)
    return _merge_sections(bucket)


def _merge_sections(bucket: dict[str, list]) -> list[dict]:
    """Merge category buckets into the ordered SECTIONS structure."""
    sections_lookup = {s["id"]: dict(s) for s in SECTIONS}
    result = []
    for sec in SECTIONS:
        sec_id = sec["id"]
        articles = bucket.get(sec_id, [])
        merged = dict(sections_lookup[sec_id])
        merged["articles"] = articles
        result.append(merged)
    return result


def _empty_sections() -> list[dict]:
    """Return sections with empty article lists."""
    return _merge_sections({})


# ── JSON helpers ──────────────────────────────────────────────────

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
