"""Configuration for AI News Daily."""

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"

# ── 五大板块定义 ─────────────────────────────
SECTIONS = [
    {"id": "headline",     "name": "要闻",     "color": "#00c896", "icon": "📰", "max": 5},
    {"id": "dev_eco",      "name": "开发生态",  "color": "#4da6ff", "icon": "🔧", "max": 5},
    {"id": "model_launch", "name": "模型发布",  "color": "#ff6b6b", "icon": "🚀", "max": 5},
    {"id": "product_app",  "name": "产品应用",  "color": "#ffa94d", "icon": "💡", "max": 5},
    {"id": "industry",     "name": "行业动态",  "color": "#b197fc", "icon": "🌐", "max": 5},
]

TARGET_TOTAL = 15       # 目标总条数
MIN_PER_SECTION = 1     # 单板块下限
MAX_PER_SECTION = 5     # 单板块上限

# 文章对象中的 category 取值
CATEGORY_VALUES = ("headline", "dev_eco", "model_launch", "product_app", "industry")

# ── 信源 → 板块映射（Fallback 用）────────────
SOURCE_CATEGORY_MAP = {
    # 官方博客 → 要闻 / 模型发布
    "OpenAI Blog":         ("headline", "model_launch"),
    "Anthropic Blog":      ("headline", "model_launch"),
    "Google DeepMind":     ("headline", "model_launch"),
    "Meta AI Blog":        ("headline", "model_launch"),
    "Microsoft AI Blog":   ("headline", "model_launch"),
    "NVIDIA AI Blog":      ("headline", "product_app"),
    # 聚合/社区
    "Techmeme":            ("headline", "industry"),
    "Ars Technica":        ("industry", "product_app"),
    "Hacker News":         ("dev_eco",  "industry"),
    "Hugging Face Papers": ("model_launch", "dev_eco"),
    # 中文站点
    "机器之心":              ("industry",     "model_launch"),
    "量子位":               ("product_app",  "headline"),
    "36氪":                 ("industry",     "product_app"),
    "AGI Hunt":            ("model_launch", "headline"),
}

# ── 原有配置（保持不变）────────────────────────
TARGET_COMPANIES = [
    "OpenAI", "Anthropic", "Google DeepMind", "Meta AI", "Microsoft AI",
    "NVIDIA AI", "ByteDance", "Alibaba", "DeepSeek", "Tencent",
    "Zhipu", "智谱", "MiniMax", "Xiaomi", "小米", "Apple AI",
    "豆包", "通义", "混元", "Mimo",
]

AI_KEYWORDS = [
    "AI", "LLM", "GPT", "Claude", "Gemini", "LLaMA",
    "大模型", "人工智能", "深度学习", "机器学习", "AGI",
    "transformer", "diffusion", "neural network", "fine-tuning",
    "RLHF", "prompt", "agent", "open source", "开源",
    "benchmark", "multimodal", "多模态", "推理", "reasoning",
    "Sora", "video generation", "视频生成", "coding", "编程",
]

RSS_FEEDS = [
    ("https://openai.com/blog/rss.xml", "OpenAI Blog"),
    ("https://www.anthropic.com/blog/rss.xml", "Anthropic Blog"),
    ("https://deepmind.google/blog/rss.xml", "Google DeepMind"),
    ("https://ai.meta.com/blog/rss/", "Meta AI Blog"),
    ("https://blogs.microsoft.com/ai/feed/", "Microsoft AI Blog"),
    ("https://blogs.nvidia.com/blog/category/ai/feed/", "NVIDIA AI Blog"),
]

REDDIT_SUBREDDITS = [
    "MachineLearning",
    "artificial",
    "OpenAI",
    "singularity",
    "LocalLLaMA",
]

# Alternative community sources (replacing Reddit)
COMMUNITY_FEEDS = [
    ("https://www.techmeme.com/feed.xml", "Techmeme"),
    ("https://feeds.arstechnica.com/arstechnica/technology", "Ars Technica"),
]
