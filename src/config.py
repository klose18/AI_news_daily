"""Configuration for AI News Daily."""

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"

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
