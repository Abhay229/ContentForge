"""
ContentForge AI - Tools Module
--------------------------------
All tools here use FREE services (no paid API keys required):
  - DuckDuckGo Search (duckduckgo-search) -> replaces paid search APIs like EXA/Serper
  - Google Trends (pytrends)              -> replaces paid trend/keyword tools like SEMrush/Ahrefs
  - textstat                              -> free local readability scoring (no API at all)

If you later want higher-quality search results, you can swap in Serper.dev's
free tier (2,500 free queries) or Tavily's free tier by editing `web_search`.
"""

import json
import time

from crewai.tools import tool

try:
    # Package was renamed from `duckduckgo-search` to `ddgs` in 2025.
    from ddgs import DDGS
except ImportError:  # pragma: no cover - fallback for older installs
    from duckduckgo_search import DDGS

from pytrends.request import TrendReq
import textstat


# ---------------------------------------------------------------------------
# 1. WEB SEARCH (free, no API key) - used by Topic Researcher & Quality Reviewer
# ---------------------------------------------------------------------------
@tool("Search the web")
def web_search(query: str) -> str:
    """Search the web for current information, news, and articles on a topic.
    Use this to find trending discussions, recent news, competitor content,
    or to fact-check claims.

    Args:
        query (str): The search query.

    Returns:
        str: JSON list of search results (title, snippet, url).
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=8))
        if not results:
            return f"No results found for '{query}'."
        cleaned = [
            {
                "title": r.get("title"),
                "snippet": r.get("body"),
                "url": r.get("href"),
            }
            for r in results
        ]
        return json.dumps(cleaned, indent=2)
    except Exception as e:
        return f"Error performing web search for '{query}': {e}"


# ---------------------------------------------------------------------------
# 2. NEWS SEARCH (free, no API key) - used by Topic Researcher
# ---------------------------------------------------------------------------
@tool("Search recent news")
def news_search(query: str) -> str:
    """Search recent news articles related to a topic. Useful for finding
    what's currently trending or being discussed about a subject.

    Args:
        query (str): The topic/keyword to search news for.

    Returns:
        str: JSON list of recent news results (title, snippet, source, date, url).
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=8))
        if not results:
            return f"No recent news found for '{query}'."
        cleaned = [
            {
                "title": r.get("title"),
                "snippet": r.get("body"),
                "source": r.get("source"),
                "date": r.get("date"),
                "url": r.get("url"),
            }
            for r in results
        ]
        return json.dumps(cleaned, indent=2)
    except Exception as e:
        return f"Error performing news search for '{query}': {e}"


# ---------------------------------------------------------------------------
# 3. GOOGLE TRENDS / KEYWORD RESEARCH (free, unofficial API, no key)
# ---------------------------------------------------------------------------
@tool("Get trending keywords")
def get_trending_keywords(topic: str) -> str:
    """Get related/rising keywords and search interest for a topic using
    Google Trends. Use this to discover what keywords are gaining momentum
    around a subject, which helps with both topic angle and SEO targeting.

    Args:
        topic (str): The seed topic or keyword.

    Returns:
        str: JSON summary of rising/top related queries and relative interest.
    """
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload([topic], timeframe="today 3-m")
        time.sleep(1)  # be polite to the free unofficial endpoint

        related = pytrends.related_queries()
        result = {"topic": topic, "top_related": [], "rising_related": []}

        topic_data = related.get(topic, {})
        top_df = topic_data.get("top")
        rising_df = topic_data.get("rising")

        if top_df is not None and not top_df.empty:
            result["top_related"] = top_df.head(10)["query"].tolist()
        if rising_df is not None and not rising_df.empty:
            result["rising_related"] = rising_df.head(10)["query"].tolist()

        interest = pytrends.interest_over_time()
        if not interest.empty:
            recent_avg = float(interest[topic].tail(4).mean())
            older_avg = float(interest[topic].head(4).mean()) or 1.0
            trend_direction = (
                "rising" if recent_avg > older_avg else "declining/stable"
            )
            result["interest_trend"] = trend_direction

        return json.dumps(result, indent=2)
    except Exception as e:
        return (
            f"Could not fetch Google Trends data for '{topic}' (this free "
            f"unofficial API is sometimes rate-limited): {e}. "
            f"Proceed using general knowledge and web_search results instead."
        )


# ---------------------------------------------------------------------------
# 4. READABILITY / CONTENT QUALITY ANALYSIS (free, fully local, no API)
# ---------------------------------------------------------------------------
@tool("Analyze readability")
def analyze_readability(text: str) -> str:
    """Analyze the readability and structural quality of a piece of text
    using standard readability formulas (Flesch Reading Ease, Flesch-Kincaid
    Grade Level, etc). Use this to check whether content is easy to read for
    the target audience.

    Args:
        text (str): The content to analyze.

    Returns:
        str: JSON with readability scores and word/sentence statistics.
    """
    try:
        scores = {
            "flesch_reading_ease": textstat.flesch_reading_ease(text),
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
            "gunning_fog_index": textstat.gunning_fog(text),
            "word_count": textstat.lexicon_count(text),
            "sentence_count": textstat.sentence_count(text),
            "estimated_reading_time_minutes": round(
                textstat.lexicon_count(text) / 200, 1
            ),
        }
        ease = scores["flesch_reading_ease"]
        if ease >= 60:
            scores["readability_verdict"] = "Easy to read - good for general audiences"
        elif ease >= 30:
            scores["readability_verdict"] = "Fairly difficult - suited for informed readers"
        else:
            scores["readability_verdict"] = "Very difficult - consider simplifying"
        return json.dumps(scores, indent=2)
    except Exception as e:
        return f"Error analyzing readability: {e}"


# ---------------------------------------------------------------------------
# 5. KEYWORD DENSITY / ON-PAGE SEO CHECK (free, fully local, no API)
# ---------------------------------------------------------------------------
@tool("Check keyword density and on-page SEO basics")
def check_keyword_density(text: str, primary_keyword: str) -> str:
    """Check how frequently the primary keyword (and its variants) appears
    in the text, and return basic on-page SEO stats such as title/word count
    guidance. Use this to validate SEO optimization work.

    Args:
        text (str): The content body to check.
        primary_keyword (str): The main target keyword/phrase.

    Returns:
        str: JSON with keyword count, density percentage, and recommendations.
    """
    try:
        words = text.lower().split()
        total_words = len(words)
        keyword_lower = primary_keyword.lower()
        occurrences = text.lower().count(keyword_lower)
        density = (occurrences / total_words * 100) if total_words else 0

        if density < 0.5:
            verdict = "Keyword density too low - consider using the keyword more naturally"
        elif density > 3:
            verdict = "Keyword density too high - risk of keyword stuffing, reduce usage"
        else:
            verdict = "Keyword density is in a healthy range"

        result = {
            "primary_keyword": primary_keyword,
            "occurrences": occurrences,
            "total_words": total_words,
            "keyword_density_percent": round(density, 2),
            "verdict": verdict,
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error checking keyword density: {e}"
