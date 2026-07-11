## 项目概述

AI 资讯日报（AI News Daily）是一个自动化工具，每天定时从多个免费来源抓取 AI 行业最新动态，通过 AI 筛选出 10 条最值得关注的资讯，生成摘要并输出为深色科技风的 HTML 网页。

## 需求汇总

| 维度 | 决策 |
|------|------|
| 推送形式 | 生成 HTML 网页，用户每天打开浏览器查看 |
| 资讯语言 | 中文 + 英文混合 |
| 资讯范围 | 聚焦国内外 AI 大厂 |
| 每日条数 | 精选 10 条 |
| 内容结构 | 标题 + 2~3 句中文摘要 + 可跳转原文链接 |
| 消息来源 | Reddit、Hacker News、公司官方博客 RSS、中文 AI 媒体 |
| 运行环境 | GitHub Actions 定时触发（每天 8:30 CST） |
| 网页托管 | GitHub Pages |
| UI 风格 | 深色主题，简洁科技风，暂不做移动端适配 |
| 历史归档 | 暂不需要 |

## 数据来源设计

### 英文来源（免费，无需 API Key）

| 来源 | 抓取方式 | 说明 |
|------|----------|------|
| Hacker News | 官方 Firebase API | 抓取热门帖子，按 AI 关键词过滤 |
| Reddit | 公共 JSON API（无需鉴权） | 监控 r/MachineLearning、r/artificial、r/OpenAI、r/singularity |
| OpenAI Blog | RSS | https://openai.com/blog/rss.xml |
| Anthropic Blog | RSS | https://www.anthropic.com/blog/rss.xml |
| Google DeepMind Blog | RSS | https://deepmind.google/blog/rss.xml |
| Meta AI Blog | RSS | https://ai.meta.com/blog/rss/ |
| Microsoft AI Blog | RSS | https://blogs.microsoft.com/ai/feed/ |
| NVIDIA AI Blog | RSS | https://blogs.nvidia.com/blog/category/ai/feed/ |

### 中文来源（免费，通过网页抓取或 RSS）

| 来源 | 抓取方式 | 说明 |
|------|----------|------|
| 机器之心 | RSS / 网页解析 | 国内头部 AI 媒体 |
| 量子位 | 网页解析 | 国内头部 AI 媒体 |
| 36氪 AI 板块 | 网页解析 | 综合科技媒体的 AI 分类 |
| AGI Hunt | 网页解析 | 专注 AGI 前沿动态的资讯平台 |

### 信息处理流程

flowchart TD
    A[GitHub Actions 定时触发<br/>每天 08:30 CST] --> B[Python 爬虫启动]
    B --> C1[抓取 Reddit API]
    B --> C2[抓取 Hacker News API]
    B --> C3[抓取各博客 RSS]
    B --> C4[抓取中文来源网页]
    C1 & C2 & C3 & C4 --> D[去重 & 清洗]
    D --> E[调用 DeepSeek API 筛选 + 生成摘要]
    E --> F[渲染 HTML 模板]
    F --> G[部署到 GitHub Pages]
    G --> H[用户打开网页即看]

## AI 摘要与筛选

从众多来源抓取到的原始数据需要经过 AI 处理，完成两件事：

1. **筛选**：从几十上百条原始资讯中，挑出 10 条最值得关注的（与大厂相关、有行业影响力）
2. **摘要**：为每一条生成 2~3 句中文摘要

**已选定方案：DeepSeek API**

DeepSeek API 中文能力强，价格极低（≈¥0.3/月），注册 https://platform.deepseek.com 即可获取 API Key，新用户有免费额度。接口兼容 OpenAI SDK 格式，接入简单。

## 重点关注的大厂列表

OpenAI、Anthropic、Google DeepMind、Meta AI、Microsoft AI、NVIDIA AI、字节豆包、阿里通义、DeepSeek、腾讯混元、智谱、MiniMax、小米 Mimo、Apple AI

## 定时运行与部署

### GitHub Actions 配置

- **触发时间**：UTC 00:30（北京时间 08:30），每周一至周五
- **运行流程**：拉代码 → 装依赖 → 跑爬虫 → 生成 HTML → 推到 GitHub Pages 分支

### GitHub Pages 托管

- HTML 生成后自动发布到 `gh-pages` 分支
- 访问地址类似：`https://你的用户名.github.io/AI_news_daily`
- 每天自动更新，用户打开即是最新内容

### 你需要准备的

| 事项 | 说明 | 费用 |
|------|------|------|
| GitHub 账号 | 注册 https://github.com | 免费 |
| 创建仓库 | 存放代码，开启 GitHub Pages | 免费 |
| DeepSeek API Key | 注册获取，存为 GitHub Secret | 几乎免费（≈¥0.3/月） |

## 项目目录结构

```
AI_news_daily/
├── .github/
│   └── workflows/
│       └── daily.yml          # GitHub Actions 定时任务配置
├── src/
│   ├── crawlers/              # 各来源爬虫
│   │   ├── hackernews.py
│   │   ├── reddit.py
│   │   ├── rss_blogs.py
│   │   └── chinese_sites.py
│   ├── curator.py             # 调用 DeepSeek 筛选 & 摘要
│   ├── render.py              # 生成 HTML
│   └── config.py               # 配置（关键词、来源列表等）
├── templates/
│   └── index.html             # HTML 模板（Jinja2）
├── output/                    # 生成的 HTML 输出目录
├── requirements.txt           # Python 依赖
├── proposal.md               # 本文档
└── README.md
```

## 技术栈

| 组件 | 选型 | 原因 |
|------|------|------|
| 语言 | Python 3.11+ | 生态丰富，爬虫/数据处理方便 |
| HTTP 请求 | `httpx` | 异步支持，API 友好 |
| RSS 解析 | `feedparser` | RSS 标准库，久经考验 |
| HTML 解析 | `BeautifulSoup4` | 中文网页抓取必备 |
| 模板渲染 | `Jinja2` | Python 标配模板引擎 |
| AI 调用 | `openai` SDK（兼容 DeepSeek） | DeepSeek 接口兼容 OpenAI 格式 |
| 调度 | GitHub Actions | 免费，稳定 |
| 托管 | GitHub Pages | 免费，自动部署 |

## 开发排期

| 阶段 | 内容 | 预计工作量 |
|------|------|------------|
| 1 | 搭建项目骨架，完成各来源爬虫 | 1 天 |
| 2 | 接入 DeepSeek API，完成筛选 + 摘要逻辑 | 0.5 天 |
| 3 | HTML 模板设计与渲染 | 0.5 天 |
| 4 | GitHub Actions + Pages 部署配置 | 0.5 天 |
| 5 | 联调测试，确保定时任务正常运行 | 0.5 天 |

## 风险与限制

| 风险 | 说明 | 应对 |
|------|------|------|
| 中文网站反爬 | 机器之心、36氪等可能封禁爬虫 | 控制频率 + 加 UA 伪装，严重时换源 |
| Reddit API 限流 | 免费接口有频率限制 | 缓存策略，每分钟不超过 10 次请求 |
| LLM 输出不稳定 | AI 摘要偶尔走样 | 代码层加格式校验，不合格时重试 |
| GitHub Actions 运行时长 | 免费版单次最长 6 小时 | 当前设计预计 2~3 分钟，远低于上限 |

---

*终版 · 需求已全部确认，进入开发阶段。*
