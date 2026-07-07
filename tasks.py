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
    "Optimize the draft article for search engines by improving its SEO while "
    "maintaining readability and natural writing.\n\n"
    "Your tasks are:\n"
    "1. Improve the article title for SEO.\n"
    "2. Improve headings where necessary.\n"
    "3. Write a compelling meta description (maximum 160 characters).\n"
    "4. Identify one primary keyword.\n"
    "5. Suggest up to five relevant secondary keywords.\n"
    "6. Naturally incorporate the keywords into the content where appropriate.\n"
    "7. Provide three concise and actionable SEO recommendations.\n\n"
    "Do not calculate keyword density.\n"
    "Do not perform readability analysis.\n"
    "Do not generate a numerical SEO score.\n"
    "Do not overuse keywords or perform keyword stuffing.\n"
    "Focus on producing content that is useful, engaging, and optimized for both readers and search engines."
),
    
    expected_output=(
    "A structured SEO report containing an optimized title, a meta description, "
    "one primary keyword, up to five secondary keywords, and three actionable "
    "SEO recommendations."
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
