# 🔥 ContentForge AI

**An autonomous multi-agent content team that researches, writes, optimizes, reviews, and repurposes content for every platform — end to end, in minutes.**

ContentForge AI is a 5-agent AI crew built with [CrewAI](https://www.crewai.com/) that automates the entire content production pipeline a marketing team runs manually today: from spotting a trending topic to publishing platform-ready posts on Twitter/X, LinkedIn, Instagram, and Facebook. It runs entirely on **free-tier / open-source infrastructure** — no paid API keys required to get started.

> Built as a showcase of production-grade multi-agent orchestration: parallel execution, structured/validated outputs, and tool-using agents — the kind of system a marketing-tech or dev-tools company could plug straight into a content workflow or offer as a product feature.

---

## 🧠 Why this matters

Content teams juggle five distinct jobs for every single piece of content: research, writing, SEO, platform adaptation, and editorial review. Usually that's five different people (or five context-switches for one overworked person). ContentForge AI turns that into a single command.

| Manual workflow | ContentForge AI |
|---|---|
| Hours of research across trend tools | Automated trend + keyword research agent |
| Draft written from scratch | Structured, on-brief article draft |
| Separate SEO audit pass | SEO scoring, meta description, keyword density — done in parallel |
| Separate editorial review pass | Fact-checking + tone/consistency review — done in parallel |
| Manually rewriting for each platform | Native Twitter thread, LinkedIn post, IG caption, FB post generated automatically |

---

## 🏗️ Architecture

Five specialized agents run in a pipeline, with independent stages **parallelized** for speed:

```
                    ┌────────────────────┐
                    │  1. Topic Researcher │   Finds trending angles,
                    │       Agent          │   keywords & context
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │  2. Content Writer   │   Drafts the article
                    │       Agent          │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                              ▼
     ┌────────────────────┐      ┌────────────────────────┐
     │ 3a. SEO Optimizer    │      │ 3b. Quality Reviewer     │   ⚡ RUN IN
     │        Agent         │      │         Agent            │   PARALLEL
     └──────────┬──────────┘      └────────────┬────────────┘
                └──────────────┬───────────────┘
                               ▼
                    ┌────────────────────────┐
                    │ 4. Social Media Adapter  │   Twitter / LinkedIn /
                    │          Agent            │   Instagram / Facebook
                    └────────────────────────┘
```

Stages 3a and 3b both only depend on the finished draft (not on each other), so they run concurrently via `ThreadPoolExecutor` — cutting real wall-clock time versus a fully sequential pipeline.

---

## 🤖 The Agent Crew

| Agent | Role | Tools |
|---|---|---|
| **Topic Researcher** | Finds trending angles, rising keywords, and relevant news for the topic | Web search, news search, Google Trends |
| **Content Writer** | Drafts a structured, engaging article from the research brief | — |
| **SEO Optimizer** | Optimizes title, meta description, and keyword usage; scores the piece | Keyword density checker, readability analyzer, Google Trends |
| **Quality Reviewer** | Fact-checks claims, checks tone/consistency, approves or flags issues | Web search, readability analyzer |
| **Social Media Adapter** | Repurposes the final article into platform-native posts | — |

Both the SEO Optimizer and Quality Reviewer return **validated, structured outputs** (Pydantic models with guardrails) — not free-text — so results are predictable and easy to plug into downstream systems (a CMS, a Slack bot, a dashboard, etc).

---

## 💸 100% Free-Tier Stack

No paid API keys are required anywhere in this project:

| Need | Paid tool it replaces | Free alternative used here |
|---|---|---|
| LLM | OpenAI GPT-4 / paid OpenRouter models | **Groq free tier** (default), OpenRouter `:free` models, or fully local **Ollama** |
| Web/news search | EXA, Serper, SerpAPI | **DuckDuckGo Search** (`ddgs`) — no key needed |
| Trend/keyword research | SEMrush, Ahrefs | **Google Trends** via `pytrends` — no key needed |
| Readability/SEO scoring | Paid SEO SaaS tools | **textstat** — local, no key needed |

You can swap any of these for a paid provider later by editing `llm_config.py` or `tools.py` — the architecture doesn't change.

---

## 🚀 Quickstart

### 1. Clone & install
```bash
git clone https://github.com/your-username/contentforge-ai.git
cd contentforge-ai
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure your free LLM key
```bash
cp .env.example .env
```
Get a **free** Groq API key at [console.groq.com/keys](https://console.groq.com/keys) (no credit card required) and paste it into `.env` as `GROQ_API_KEY`. (OpenRouter free models and fully-local Ollama are also supported — see `.env.example`.)

### 3. Run the pipeline
```bash
python main.py --topic "AI agents in customer support" \
                --industry "SaaS" \
                --audience "B2B marketing managers" \
                --word-count 900
```

### 4. Check the output
```
drafts/article_draft.md          # the raw article draft
outputs/seo_report.md            # SEO title, meta description, keyword data, score
outputs/quality_review.md        # accuracy/consistency scores, flagged issues
outputs/social_media_pack.md     # Twitter thread, LinkedIn, Instagram, Facebook posts
```

---

## 🖥️ Dashboard (no CLI needed)

Prefer a UI? Launch the Streamlit dashboard instead of the CLI:

```bash
streamlit run streamlit_app.py
```

Fill in the topic, industry, audience, and word count in the sidebar, hit **Run Pipeline**, and watch each phase execute live with progress updates. Results land in tabs: **Draft**, **SEO Report**, **Quality Review**, and **Social Media Pack** — each rendered as formatted Markdown, ready to copy and publish.

This is the piece you'd demo to a client or embed in an internal tool — same pipeline, zero terminal required.

---

## ⚙️ CLI Options

| Flag | Default | Description |
|---|---|---|
| `--topic` | *(required)* | The topic/subject to create content about |
| `--industry` | `Technology` | Industry or niche context |
| `--audience` | `general professional audience` | Target audience description |
| `--word-count` | `800` | Target article length |
| `--year` | `2026` | Current year context for the agents |

---

## 🧩 Extending the Project

This is designed to be a foundation, not a finished black box:

- **Add a platform** — extend `SocialMediaPack` in `tasks.py` and the Social Media Adapter's task description (e.g. add TikTok scripts or YouTube descriptions).
- **Add a review gate** — plug a human-in-the-loop approval step between Phase 3 and Phase 4 before publishing.
- **Swap in real publishing** — connect the final outputs to Buffer, Zapier, or platform APIs to auto-publish.
- **Swap the LLM** — point `llm_config.py` at any provider CrewAI/LiteLLM supports, paid or free.
- **Batch mode** — loop `run_pipeline()` over a CSV of topics for bulk content generation.

---

## 📁 Project Structure

```
contentforge-ai/
├── agents.py          # 5 agent definitions
├── tasks.py           # Task definitions, Pydantic schemas & guardrails
├── tools.py           # Free-tier tools (search, trends, readability, SEO)
├── llm_config.py       # Pluggable free LLM backend (Groq/OpenRouter/Ollama)
├── main.py            # Pipeline orchestration with parallel execution (CLI)
├── streamlit_app.py    # Dashboard UI for the pipeline
├── requirements.txt
├── .env.example
├── drafts/             # Generated article drafts land here
├── outputs/             # Generated SEO/review/social outputs land here
└── task_outputs/        # Raw CrewAI task logs
```

---

## 🛣️ Roadmap Ideas

- [x] Web dashboard (Streamlit) to trigger runs and preview outputs
- [ ] Multi-topic batch generation
- [ ] Direct publish integrations (WordPress, Buffer, Notion)
- [ ] Human-in-the-loop approval step before social posting
- [ ] Support for video script / YouTube description generation

---

## 📄 License

MIT — see [LICENSE](LICENSE). Free to use, modify, and build on for personal or commercial products.
