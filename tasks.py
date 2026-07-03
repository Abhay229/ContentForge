import os
from typing import Any, List, Tuple

from crewai import Task
from crewai.tasks.task_output import TaskOutput
from pydantic import BaseModel, Field

from agents import (
    content_writer,
    quality_reviewer,
    seo_optimizer,
    social_media_adapter,
    topic_researcher,
)

os.makedirs("task_outputs", exist_ok=True)
os.makedirs("drafts", exist_ok=True)
os.makedirs("outputs", exist_ok=True)


# ---------------------------------------------------------------------------
# Structured output models
# ---------------------------------------------------------------------------
class SEOReport(BaseModel):
    optimized_title: str = Field(description="SEO-optimized title (under 60 chars)")
    meta_description: str = Field(description="Meta description (under 160 chars)")
    primary_keyword: str = Field(description="Primary target keyword")
    secondary_keywords: List[str] = Field(description="Supporting keywords")
    seo_score: float = Field(description="Overall SEO score 0-100")
    recommendations: List[str] = Field(description="Further SEO recommendations")


class QualityReview(BaseModel):
    approved: bool = Field(description="Whether the content is approved to publish")
    accuracy_score: float = Field(description="Factual accuracy score 0.0 to 1.0")
    consistency_score: float = Field(description="Tone/style consistency score 0.0 to 1.0")
    issues_found: List[str] = Field(description="List of issues found, empty if none")
    suggestions: List[str] = Field(description="Suggestions for improvement")


class SocialMediaPack(BaseModel):
    twitter_thread: List[str] = Field(description="A thread of tweets, each under 280 chars")
    linkedin_post: str = Field(description="A professional LinkedIn post")
    instagram_caption: str = Field(description="An Instagram caption with relevant hashtags")
    facebook_post: str = Field(description="A conversational Facebook post")


# ---------------------------------------------------------------------------
# Guardrails
# ---------------------------------------------------------------------------
def validate_seo_report(result: TaskOutput) -> Tuple[bool, Any]:
    rep = result.pydantic
    if not rep:
        return (False, "SEO report must be structured output.")
    if len(rep.optimized_title) > 70:
        return (False, "Optimized title should be under ~60-70 characters.")
    if not (0 <= rep.seo_score <= 100):
        return (False, "SEO score must be between 0 and 100.")
    return (True, rep)


def validate_quality_review(result: TaskOutput) -> Tuple[bool, Any]:
    rev = result.pydantic
    if not rev:
        return (False, "Quality review must be structured output.")
    if not (0 <= rev.accuracy_score <= 1) or not (0 <= rev.consistency_score <= 1):
        return (False, "Scores must be between 0.0 and 1.0.")
    return (True, rev)


def validate_social_pack(result: TaskOutput) -> Tuple[bool, Any]:
    pack = result.pydantic
    if not pack:
        return (False, "Social media pack must be structured output.")
    for tweet in pack.twitter_thread:
        if len(tweet) > 280:
            return (False, f"Tweet exceeds 280 characters: '{tweet[:40]}...'")
    if len(pack.twitter_thread) < 1:
        return (False, "Must include at least 1 tweet.")
    return (True, pack)


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------
research_topic_task = Task(
    description=(
        "Research the topic '{topic}' within the '{industry}' industry for an "
        "audience of {target_audience}. Find: (1) trending angles/subtopics "
        "people are currently discussing, (2) high-value keywords and rising "
        "search queries, (3) any recent news relevant to this topic. Use the "
        "current year as {current_year}."
    ),
    expected_output=(
        "A research brief containing: 3-5 trending angles on the topic, a list "
        "of primary and secondary keywords with any trend signal found, and a "
        "short summary of relevant recent news/context."
    ),
    agent=topic_researcher,
)

write_content_task = Task(
    description=(
        "Using the research brief, write a complete, well-structured draft "
        "article about '{topic}' for {target_audience}. Target length: "
        "{word_count} words. Include an engaging title, an intro hook, clear "
        "subheadings, and a strong conclusion with a call to action."
    ),
    expected_output=(
        "A complete draft article in Markdown with title, headings, and body "
        "text, ready for SEO optimization and review."
    ),
    agent=content_writer,
    context=[research_topic_task],
    output_file="drafts/article_draft.md",
)

seo_optimize_task = Task(
    description=(
        "Optimize the draft article for search engines. Refine the title and "
        "add a meta description, identify the primary and secondary keywords, "
        "check keyword density and readability using your tools, and give an "
        "overall SEO score with concrete recommendations. Do not sacrifice "
        "readability for keyword stuffing."
    ),
    expected_output=(
        "A structured SEO report with optimized title, meta description, "
        "primary/secondary keywords, SEO score, and recommendations."
    ),
    agent=seo_optimizer,
    context=[write_content_task],
    output_pydantic=SEOReport,
    guardrail=validate_seo_report,
    output_file="outputs/seo_report.md",
)

quality_review_task = Task(
    description=(
        "Review the draft article for factual accuracy (spot-check any claims "
        "using web search), tone/style consistency, grammar, and overall "
        "publish-readiness. List any issues found and whether the piece is "
        "approved."
    ),
    expected_output=(
        "A structured quality review with approval status, accuracy and "
        "consistency scores, issues found, and improvement suggestions."
    ),
    agent=quality_reviewer,
    context=[write_content_task],
    output_pydantic=QualityReview,
    guardrail=validate_quality_review,
    output_file="outputs/quality_review.md",
)

social_adapt_task = Task(
    description=(
        "Using the SEO-optimized article details and the quality review "
        "feedback, repurpose the article into platform-native content for: "
        "a Twitter/X thread (3-6 tweets), a LinkedIn post, an Instagram "
        "caption (with hashtags), and a Facebook post. Match each platform's "
        "tone and constraints. Incorporate the optimized title/keywords "
        "naturally, and address any issues raised in the quality review."
    ),
    expected_output=(
        "A structured social media pack with a Twitter thread, LinkedIn post, "
        "Instagram caption, and Facebook post - each ready to publish."
    ),
    agent=social_media_adapter,
    context=[seo_optimize_task, quality_review_task],
    output_pydantic=SocialMediaPack,
    guardrail=validate_social_pack,
    output_file="outputs/social_media_pack.md",
)
