"""
ContentForge AI - Dashboard
------------------------------
A simple Streamlit UI to trigger the content pipeline and view results
without touching the CLI. Run with:

    streamlit run streamlit_app.py
"""

import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import streamlit as st

from main import (
    research_crew,
    review_crew,
    run_crew_task,
    seo_crew,
    social_crew,
    writer_crew,
)

st.set_page_config(page_title="ContentForge AI", page_icon="🔥", layout="wide")

DRAFT_FILE = Path("drafts/article_draft.md")
SEO_FILE = Path("outputs/seo_report.md")
REVIEW_FILE = Path("outputs/quality_review.md")
SOCIAL_FILE = Path("outputs/social_media_pack.md")


def read_if_exists(path: Path) -> str:
    return path.read_text() if path.exists() else "*Not generated yet.*"


# ---------------------------------------------------------------------------
# Sidebar - pipeline inputs
# ---------------------------------------------------------------------------
st.sidebar.title("🔥 ContentForge AI")
st.sidebar.caption("Intelligent multi-agent content creation pipeline")

with st.sidebar.form("pipeline_form"):
    topic = st.text_input("Topic", placeholder="e.g. AI agents in customer support")
    industry = st.text_input("Industry / niche", value="Technology")
    audience = st.text_input("Target audience", value="general professional audience")
    word_count = st.number_input("Target word count", min_value=200, max_value=3000, value=800, step=100)
    year = st.text_input("Current year context", value="2026")
    submitted = st.form_submit_button("🚀 Run Pipeline", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Free-tier stack:** Groq/OpenRouter/Ollama LLM · DuckDuckGo search · "
    "Google Trends · textstat readability — no paid API keys required."
)

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
st.title("ContentForge AI Dashboard")
st.caption(
    "Research → Write → (SEO + Review in parallel) → Social Media Adaptation"
)

tab_draft, tab_seo, tab_review, tab_social = st.tabs(
    ["📝 Draft", "🔍 SEO Report", "✅ Quality Review", "📱 Social Media Pack"]
)

if submitted:
    if not topic.strip():
        st.error("Please enter a topic before running the pipeline.")
    else:
        pipeline_input = {
            "topic": topic,
            "industry": industry,
            "target_audience": audience,
            "word_count": str(word_count),
            "current_year": year,
        }

        progress = st.progress(0, text="Starting pipeline...")
        status = st.status("Running ContentForge AI pipeline...", expanded=True)

        try:
            status.write("🔎 Phase 1: Topic Research...")
            run_crew_task(research_crew, pipeline_input, "Topic Research")
            progress.progress(20, text="Research complete")

            status.write("✍️ Phase 2: Content Writing...")
            run_crew_task(writer_crew, pipeline_input, "Content Writing")
            progress.progress(45, text="Draft complete")

            status.write("⚡ Phase 3: SEO Optimization & Quality Review (parallel)...")
            with ThreadPoolExecutor(max_workers=2) as executor:
                seo_future = executor.submit(
                    run_crew_task, seo_crew, pipeline_input, "SEO Optimization"
                )
                review_future = executor.submit(
                    run_crew_task, review_crew, pipeline_input, "Quality Review"
                )
                seo_future.result()
                review_future.result()
            progress.progress(75, text="SEO + Review complete")

            status.write("📱 Phase 4: Social Media Adaptation...")
            run_crew_task(social_crew, pipeline_input, "Social Media Adaptation")
            progress.progress(100, text="Pipeline complete!")

            status.update(label="✅ Pipeline complete!", state="complete")
        except Exception as e:
            status.update(label="❌ Pipeline failed", state="error")
            st.error(f"Pipeline error: {e}")

# ---------------------------------------------------------------------------
# Display outputs (persist across reruns by reading from disk)
# ---------------------------------------------------------------------------
with tab_draft:
    st.markdown(read_if_exists(DRAFT_FILE))

with tab_seo:
    st.markdown(read_if_exists(SEO_FILE))

with tab_review:
    st.markdown(read_if_exists(REVIEW_FILE))

with tab_social:
    st.markdown(read_if_exists(SOCIAL_FILE))
