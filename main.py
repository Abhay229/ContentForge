import argparse
import time
from concurrent.futures import ThreadPoolExecutor

from crewai import Crew, Process

from agents import (
    content_writer,
    quality_reviewer,
    seo_optimizer,
    social_media_adapter,
    topic_researcher,
)
from tasks import (
    quality_review_task,
    research_topic_task,
    seo_optimize_task,
    social_adapt_task,
    write_content_task,
)

# ---------------------------------------------------------------------------
# Crews - one crew per stage so we can control sequencing & parallelism
# ---------------------------------------------------------------------------
research_crew = Crew(
    agents=[topic_researcher],
    tasks=[research_topic_task],
    verbose=True,
    process=Process.sequential,
    cache=True,
    max_rpm=15,
)

writer_crew = Crew(
    agents=[content_writer],
    tasks=[write_content_task],
    verbose=True,
    process=Process.sequential,
    cache=True,
    max_rpm=15,
)

# These two run IN PARALLEL - both only need the finished draft, not each other
seo_crew = Crew(
    agents=[seo_optimizer],
    tasks=[seo_optimize_task],
    verbose=True,
    process=Process.sequential,
    cache=True,
    max_rpm=12,
)

review_crew = Crew(
    agents=[quality_reviewer],
    tasks=[quality_review_task],
    verbose=True,
    process=Process.sequential,
    cache=True,
    max_rpm=12,
)

social_crew = Crew(
    agents=[social_media_adapter],
    tasks=[social_adapt_task],
    verbose=True,
    process=Process.sequential,
    cache=True,
    max_rpm=15,
)


def run_crew_task(crew, inputs, task_name):
    """Helper function to run a crew task with logging."""
    print(f"🚀 Starting {task_name}...")
    result = crew.kickoff(inputs=inputs)
    print(f"✅ Completed {task_name}")
    return result


def run_pipeline(pipeline_input):
    """Run the full content pipeline, parallelizing SEO + Quality Review."""
    timings = {}

    # Phase 1: Topic Research
    print("\n🔎 Phase 1: Topic Research...")
    t0 = time.time()
    run_crew_task(research_crew, pipeline_input, "Topic Research")
    timings["research"] = time.time() - t0
    print(f"✅ Phase 1 completed in {timings['research']:.2f}s")

    # Phase 2: Content Writing (depends on research)
    print("\n✍️  Phase 2: Content Writing...")
    t0 = time.time()
    run_crew_task(writer_crew, pipeline_input, "Content Writing")
    timings["writing"] = time.time() - t0
    print(f"✅ Phase 2 completed in {timings['writing']:.2f}s")

    # Phase 3: SEO Optimization + Quality Review IN PARALLEL (both depend
    # only on the draft, not on each other)
    print("\n⚡ Phase 3: SEO Optimization & Quality Review (parallel)...")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=2) as executor:
        seo_future = executor.submit(
            run_crew_task, seo_crew, pipeline_input, "SEO Optimization"
        )
        review_future = executor.submit(
            run_crew_task, review_crew, pipeline_input, "Quality Review"
        )
        seo_future.result()
        review_future.result()
    timings["seo_and_review_parallel"] = time.time() - t0
    print(f"✅ Phase 3 completed in {timings['seo_and_review_parallel']:.2f}s")

    # Phase 4: Social Media Adaptation (depends on Phase 3 results)
    print("\n📱 Phase 4: Social Media Adaptation...")
    t0 = time.time()
    run_crew_task(social_crew, pipeline_input, "Social Media Adaptation")
    timings["social_adapt"] = time.time() - t0
    print(f"✅ Phase 4 completed in {timings['social_adapt']:.2f}s")

    return timings


def main():
    parser = argparse.ArgumentParser(
        description="ContentForge AI - Intelligent Content Creation Pipeline"
    )
    parser.add_argument("--topic", required=True, help="Topic to create content about")
    parser.add_argument(
        "--industry", default="Technology", help="Industry/niche context (default: Technology)"
    )
    parser.add_argument(
        "--audience",
        default="general professional audience",
        help="Target audience description",
    )
    parser.add_argument(
        "--word-count", default="800", help="Target article word count (default: 800)"
    )
    parser.add_argument(
        "--year", default="2026", help="Current year for context (default: 2026)"
    )

    args = parser.parse_args()

    pipeline_input = {
        "topic": args.topic,
        "industry": args.industry,
        "target_audience": args.audience,
        "word_count": args.word_count,
        "current_year": args.year,
    }

    print(f"\n📋 ContentForge AI Pipeline")
    print(f"   Topic: {args.topic}")
    print(f"   Industry: {args.industry}")
    print(f"   Audience: {args.audience}\n")

    start = time.time()
    timings = run_pipeline(pipeline_input)
    total_time = time.time() - start

    sequential_estimate = sum(timings.values()) + timings["seo_and_review_parallel"]
    time_saved = sequential_estimate - total_time

    print("\n🎉 Content pipeline completed!")
    for stage, t in timings.items():
        print(f"⏱️  {stage}: {t:.2f}s")
    print(f"⏱️  Total execution time: {total_time:.2f}s ({total_time/60:.2f} min)")
    print(f"💡 Estimated time saved via parallel execution: {time_saved:.2f}s")
    print("\n📂 Outputs saved to: drafts/, outputs/")


if __name__ == "__main__":
    main()
