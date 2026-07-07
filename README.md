# ContentForge AI

Content creation is rarely limited by ideas. It is limited by workflow: too many handoffs, too many tools, and too much repetitive work between research and publication. ContentForge AI collapses that sprawl into one coordinated multi-agent system that researches, writes, reviews, optimizes, and repurposes content in a single run.

Built with CrewAI, it gives you a five-agent content team behind both a CLI and a Streamlit dashboard, powered by a stack that can stay fully free-tier or go fully local.

## Why This Matters

Every serious content workflow includes the same hard parts: finding the right angle, shaping a draft, tightening SEO, checking quality, and adapting the final piece for distribution. In most teams, those jobs happen in separate passes across separate tools. The result is slower output, more context switching, and more room for inconsistencies.

ContentForge AI turns those handoffs into a pipeline. Research feeds writing. Writing feeds SEO and editorial review. The reviewed article becomes platform-ready social copy without anyone restarting the process from scratch.

| Manual workflow | ContentForge AI |
| --- | --- |
| Research done across multiple tabs and tools | Topic research agent gathers web, news, and trend context |
| Drafting starts from a blank page | Writer starts from a research brief with audience and industry context |
| SEO is a separate pass after the draft | Dedicated SEO agent produces structured optimization output |
| Editorial review happens late and inconsistently | Quality reviewer runs as a defined pipeline stage |
| Social copy is rewritten manually for each platform | Social media agent creates a full repurposing pack |

## Architecture

Five agents. Four execution phases. One clean content pipeline.

The pipeline is split into four execution phases powered by five specialized agents:

1. Topic Researcher gathers trend, keyword, and news context.
2. Content Writer turns the research brief into a draft article.
3. SEO Optimizer and Quality Reviewer run in parallel against the completed draft.
4. Social Media Adapter repurposes the reviewed content into platform-specific posts.

```text
Input: topic + industry + audience
                 |
                 v
     +---------------------------+
     |      Topic Researcher     |
     |   Trends, keywords, news  |
     +---------------------------+
                 |
                 v
     +---------------------------+
     |       Content Writer      |
     |     Drafts the article    |
     +---------------------------+
                 |
        Runs in parallel
          /             \
         v               v
+----------------+   +-------------------+
| SEO Optimizer  |   | Quality Reviewer  |
| Keywords, meta |   | Accuracy & tone   |
| and SEO output |   | check             |
+----------------+   +-------------------+
          \             /
           v           v
     +---------------------------+
     |    Social Media Adapter   |
     |  Twitter, LinkedIn, IG,   |
     |            FB             |
     +---------------------------+
                 |
                 v
 Output: article + social media pack

[Parallel phase] SEO Optimizer + Quality Reviewer run concurrently
```

The parallel section is deliberate. SEO optimization and quality review both depend on the written draft, but neither depends on the other. In `main.py`, they are launched with `ThreadPoolExecutor`, and the second task is slightly staggered to reduce pressure on free-tier limits. That shortens wall-clock runtime without compromising the logical order of the workflow.

The rest of the pipeline stays sequential because those stages have true dependencies: writing needs research, and social adaptation needs both the SEO and review outputs.

## Agent Flow

| Agent | Role | Goal | Tools used |
| --- | --- | --- | --- |
| Topic Researcher | Research strategist | Discover trending angles, useful keywords, and recent context for the topic and industry | `web_search`, `news_search`, `get_trending_keywords` |
| Content Writer | Draft author | Write a structured article tailored to the target audience using the research brief | None |
| SEO Optimizer | Search optimization specialist | Improve search-friendliness without sacrificing readability or natural writing | `get_trending_keywords` |
| Quality Reviewer | Editorial gatekeeper | Review factual accuracy, tone consistency, grammar, and publish-readiness | `web_search` |
| Social Media Adapter | Distribution specialist | Repurpose the article into native posts for Twitter/X, LinkedIn, Instagram, and Facebook | None |

## 100% Free-Tier Stack

This project was built to prove that a credible multi-agent content system does not need a paid stack to be useful.

| Capability | Common paid option | Free replacement used here |
| --- | --- | --- |
| LLM inference | OpenAI GPT-4-class paid APIs | Groq free tier, OpenRouter free models, or local Ollama via `llm_config.py` |
| Web search | Exa, Serper, SerpAPI | DuckDuckGo search through `ddgs` |
| News discovery | Paid search/news APIs | DuckDuckGo news search through `ddgs` |
| Trend and keyword research | Ahrefs, SEMrush | Google Trends through `pytrends` |
| Readability analysis | Paid SEO/content suites | Local `textstat` utility |

## Privacy & Local-First

If you want zero external data exposure, the architecture supports it.

By setting `LLM_PROVIDER=ollama`, ContentForge AI can run with a local Ollama model instead of a hosted API. In that setup, LLM inference stays on the machine. No model prompts or completions need to leave your system for the language model layer.

| Mode | What stays local | What to know |
| --- | --- | --- |
| `ollama` | LLM inference and generated content | Requires Ollama installed locally and a model pulled in advance |
| `groq` or `openrouter` | Local orchestration, task logic, and file outputs | LLM requests are sent to the selected hosted provider |

The rest of the project is already file-based and local by design: outputs are written to `drafts/`, `outputs/`, and `task_outputs/` in the repo workspace.

## Features

The engineering here is practical, not decorative: structured outputs where downstream reliability matters, free tooling where it saves cost, and just enough orchestration to make the system feel cohesive instead of fragile.

| Feature | Implemented |
| --- | --- |
| Five-agent CrewAI pipeline for research, drafting, SEO, review, and social repurposing | Yes |
| Parallel execution for SEO and quality review | Yes |
| Staggered cooldowns between phases to respect free-tier limits | Yes |
| Configurable LLM provider selection via environment variables | Yes |
| Groq, OpenRouter, and Ollama support | Yes |
| Structured Pydantic outputs for SEO, quality review, and social media packaging | Yes |
| Guardrail validation functions on structured task outputs | Yes |
| CLI entrypoint for scripted runs | Yes |
| Streamlit dashboard for interactive runs | Yes |
| File-based output artifacts in `drafts/`, `outputs/`, and `task_outputs/` | Yes |
| Built-in free search, trends, readability, and keyword-density utilities | Yes |

## Reliability & Security

The project already includes several engineering choices that make it safer and more dependable to run, especially on free-tier infrastructure.

| Area | What is implemented |
| --- | --- |
| Secrets handling | LLM credentials are loaded from environment variables via `.env`; keys are not hardcoded in the source |
| Output validation | SEO, quality review, and social outputs use Pydantic schemas plus guardrail validation functions |
| Rate-limit awareness | The pipeline applies cooldowns between phases and staggers parallel task startup to reduce pressure on free-tier providers |
| Failure boundaries | Outputs are written to files by stage, which makes runs easier to inspect and recover from manually |

One important accuracy note: the current codebase does not implement automatic retry with exponential backoff yet. It does include cooldown-based pacing and staggered parallel execution, but true retry/backoff logic would be a future enhancement rather than a present feature.

## Quickstart

From clone to first run takes only a few minutes.

### 1. Clone the repository

```bash
git clone https://github.com/your-username/contentforge-ai.git
cd contentforge-ai
```

### 2. Create an environment and install dependencies

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

### 3. Configure `.env`

Copy the example file.

Windows:

```bash
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Set `LLM_PROVIDER` to one of:

| Provider | What you need |
| --- | --- |
| `groq` | A free Groq API key |
| `openrouter` | A free OpenRouter API key |
| `ollama` | Local Ollama installed and a model pulled |

Key environment variables available in `.env.example`:

| Variable | Purpose |
| --- | --- |
| `LLM_PROVIDER` | Selects `groq`, `openrouter`, or `ollama` |
| `GROQ_API_KEY` | Groq API key |
| `GROQ_MODEL` | Groq model name |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `OPENROUTER_MODEL` | OpenRouter model name |
| `OLLAMA_MODEL` | Local Ollama model identifier |
| `OLLAMA_BASE_URL` | Ollama base URL |

Optional runtime tuning:

| Variable | Default | Purpose |
| --- | --- | --- |
| `PHASE_COOLDOWN_SECONDS` | `12` | Pause between pipeline phases to reduce rate-limit pressure |

### 4. Run the CLI pipeline

```bash
python main.py --topic "AI agents in customer support" --industry "SaaS" --audience "B2B marketing managers" --word-count 900
```

### 5. Run the Streamlit dashboard

```bash
streamlit run streamlit_app.py
```

## CLI Flags

The CLI is intentionally small: just enough control to steer the run without turning the project into a maze of switches.

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `--topic` | Yes | None | Topic to create content about |
| `--industry` | No | `Technology` | Industry or niche context |
| `--audience` | No | `general professional audience` | Target audience description |
| `--word-count` | No | `800` | Target article length |
| `--year` | No | `2026` | Year context passed into the research stage |

## Outputs

Every run leaves a paper trail on disk, which makes the system easier to inspect, reuse, and integrate into larger workflows.

| Path | Description |
| --- | --- |
| `drafts/article_draft.md` | Article draft generated by the writing stage |
| `outputs/seo_report.md` | Structured SEO output written by the SEO stage |
| `outputs/quality_review.md` | Structured quality review output |
| `outputs/social_media_pack.md` | Repurposed posts for supported platforms |
| `task_outputs/` | Task output directory created by the task layer |

## Project Structure

The repo is compact. Most of the core behavior lives in a handful of files, which makes it approachable to extend.

| Path | Description |
| --- | --- |
| `agents.py` | Defines the five CrewAI agents and their goals, backstories, and tool assignments |
| `tasks.py` | Declares task prompts, Pydantic schemas, guardrails, and output destinations |
| `tools.py` | Implements free web search, news search, trend lookup, readability analysis, and keyword-density tools |
| `llm_config.py` | Selects and configures the LLM backend from environment variables |
| `main.py` | CLI entrypoint and pipeline orchestrator, including the parallel execution phase |
| `streamlit_app.py` | Streamlit interface for running the pipeline interactively and viewing saved outputs |
| `requirements.txt` | Python dependency list |
| `.env.example` | Example environment configuration for supported LLM providers |
| `.gitignore` | Ignore rules for secrets, environments, and generated output files |
| `LICENSE` | MIT license for the project |
| `drafts/` | Generated draft content directory |
| `outputs/` | Generated SEO, review, and social output directory |
| `task_outputs/` | Generated CrewAI task-output directory |

## Extending the Project

This is the kind of project that invites expansion. The foundations are already in place for a more production-grade content engine.

| Extension idea | What it would build on |
| --- | --- |
| Add new channels such as TikTok, YouTube, or email | Extend `SocialMediaPack` and the social adaptation task in `tasks.py` |
| Introduce human approval before social adaptation | Insert a manual checkpoint between the review/SEO phase and the social phase |
| Add publishing integrations | Push outputs to a CMS, scheduler, or social API after generation |
| Add batch processing | Wrap `run_pipeline()` in a loop for multiple topics or CSV-driven runs |
| Strengthen evaluation | Expand guardrails and add automated scoring or regression tests around task outputs |
| Swap the model provider | Change `.env` or expand `llm_config.py` for additional LiteLLM-compatible backends |

## Roadmap

The current version is already useful. The next step is making it broader, deeper, and easier to operationalize.

- Add batch generation for multiple topics in one run
- Add optional publishing integrations for CMS or social scheduling tools
- Add a human-in-the-loop approval gate before final distribution
- Expand supported output formats beyond article plus social copy
- Add stronger automated validation and tests around structured task outputs

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for the full text.
