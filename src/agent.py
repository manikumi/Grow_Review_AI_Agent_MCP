import json
import os
from datetime import date, datetime
from typing import Any, Callable, Dict, Optional

from rich.console import Console

from src.ingestion.fetcher import fetch_reviews
from src.processing.clusterer import cluster_themes
from src.processing.pulse_generator import generate_pulse, render_pulse
from src.processing.scrubber import scrub
from src.utils.config import GROWW_APP_ID, REVIEW_LOOKBACK_WEEKS, REVIEW_MAX_COUNT

console = Console()


def run_pipeline(
    lookback_weeks: Optional[int] = None,
    max_count: Optional[int] = None,
    app_id: Optional[str] = None,
    deliver_mcp: bool = True,
    callback: Optional[Callable[[str, str, str, Optional[Dict[str, Any]]], None]] = None,
) -> Dict[str, Any]:
    """
    Runs the full end-to-end Groww Review AI Agent pipeline:
    fetch -> scrub -> cluster -> generate_pulse -> render_pulse -> deliver

    Supports real-time callback: callback(step_id, status, log_message, payload)
    Returns structured results dictionary for API and frontend display.
    """
    def log(step_id: str, status: str, message: str, payload: Optional[Dict[str, Any]] = None):
        console.print(f"[{'bold magenta' if status == 'running' else 'green'}][{step_id.upper()}] {message}[/]")
        if callback:
            try:
                callback(step_id, status, message, payload)
            except Exception as e:
                console.print(f"[yellow]Callback error: {e}[/yellow]")

    lookback = lookback_weeks or REVIEW_LOOKBACK_WEEKS
    count = max_count or REVIEW_MAX_COUNT
    target_app_id = app_id or GROWW_APP_ID

    log("init", "running", f"Starting Groww Review AI Agent (Lookback: {lookback}w, Target App: {target_app_id})...")

    # 1. Fetch
    log("fetch", "running", f"Step 1: Fetching up to {count} reviews from Google Play Store...")
    try:
        raw_reviews = fetch_reviews(target_app_id, lookback_weeks=lookback, max_count=count)
    except Exception as e:
        log("fetch", "error", f"Error fetching reviews: {e}")
        raw_reviews = []

    if not raw_reviews:
        log("fetch", "error", "No reviews fetched. Exiting pipeline.")
        return {"success": False, "error": "No reviews fetched"}

    log("fetch", "done", f"Fetched {len(raw_reviews)} valid reviews from Google Play Store.")

    # 2. Scrub
    log("scrub", "running", "Step 2: Scrubbing PII and assigning SHA-256 anonymized IDs...")
    clean_reviews = scrub(raw_reviews)
    scrubbed_count = len(raw_reviews) - len(clean_reviews)
    log("scrub", "running", f"Scrubbed {scrubbed_count} reviews completely. {len(clean_reviews)} remain.")

    if not clean_reviews:
        log("scrub", "error", "No clean reviews left after scrubbing.")
        return {"success": False, "error": "No clean reviews left after scrubbing"}

    # Guard to stay strictly under the 2K token limit
    if len(clean_reviews) > 8:
        log("scrub", "running", f"Capping to top 8 reviews to stay strictly within 2K Groq token limit.")
        processed_reviews = clean_reviews[:8]
    else:
        processed_reviews = clean_reviews

    log("scrub", "done", f"Scrubbing complete. {len(processed_reviews)} reviews queued for clustering.")

    # 3. Cluster Themes
    log("cluster", "running", "Step 3: Clustering Themes via Groq LLM...")
    try:
        clusters = cluster_themes(processed_reviews)
    except Exception as e:
        log("cluster", "error", f"LLM clustering encountered an error: {e}")
        from src.processing.clusterer import ThemeCluster
        clusters = [ThemeCluster(name="General Feedback", review_ids=[r.id for r in processed_reviews], count=len(processed_reviews), summary="User feedback and general reactions.")]

    log("cluster", "done", f"Discovered {len(clusters)} distinct themes: {', '.join([c.name for c in clusters])}")

    # 4. Generate Pulse
    log("pulse", "running", "Step 4: Generating Weekly Pulse & Action Ideas...")
    pulse = generate_pulse(clusters, processed_reviews)
    log("pulse", "done", f"Pulse generated with {len(pulse.action_ideas)} action ideas and {len(pulse.user_quotes)} quotes.")

    # 5. Render Markdown
    log("render", "running", "Step 5: Rendering Markdown Report (<=250 words)...")
    md_output = render_pulse(pulse)
    log("render", "done", f"Markdown rendered successfully ({pulse.word_count} words).")

    # 6. Delivery via MCP
    log("deliver", "running", "Step 6: Delivering via MCP (Google Docs & Gmail)...")
    doc_url = ""
    draft_id = ""

    if deliver_mcp:
        try:
            from src.mcp.router import mcp_router
            from src.utils.config import PULSE_RECIPIENT_EMAIL

            today_str = date.today().isoformat()
            doc_title = f"Groww Weekly Pulse - {today_str}"

            log("deliver", "running", f"Appending '{doc_title}' to Google Doc via MCP...")
            try:
                doc_url = mcp_router.create_doc(title=doc_title, content=md_output)
                log("deliver", "running", f"Google Doc updated: {doc_url}")
            except Exception as doc_err:
                doc_url = ""
                log("deliver", "error", f"Google Doc update failed: {doc_err}")

            if PULSE_RECIPIENT_EMAIL:
                log("deliver", "running", f"Drafting Gmail message to {PULSE_RECIPIENT_EMAIL}...")
                draft_id = mcp_router.create_gmail_draft(to=PULSE_RECIPIENT_EMAIL, doc_url=doc_url, pulse_content=md_output)
                log("deliver", "done", f"Gmail draft created: {draft_id}")
            else:
                log("deliver", "done", f"Doc created. No PULSE_RECIPIENT_EMAIL configured, skipping email.")
        except Exception as e:
            log("deliver", "error", f"Failed to deliver via MCP: {e}. Fallback to local save.")
    else:
        log("deliver", "done", "MCP delivery skipped by request.")

    # Always persist locally to output/
    os.makedirs("output", exist_ok=True)
    today_iso = date.today().isoformat()
    md_filepath = os.path.join("output", f"pulse_{today_iso}.md")
    with open(md_filepath, "w", encoding="utf-8") as f:
        f.write(md_output)

    # Calculate average rating
    ratings = [r.rating for r in raw_reviews if r.rating is not None]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 4.0

    # Build structured response
    top_themes_data = []
    total_processed = max(1, len(processed_reviews))
    for c in pulse.top_themes:
        top_themes_data.append({
            "name": c.name,
            "count": c.count,
            "percentage": round((c.count / total_processed) * 100),
            "summary": c.summary,
            "review_ids": c.review_ids,
        })

    all_themes_data = []
    for c in clusters:
        all_themes_data.append({
            "name": c.name,
            "count": c.count,
            "percentage": round((c.count / total_processed) * 100),
            "summary": c.summary,
            "review_ids": c.review_ids,
        })

    result_data = {
        "success": True,
        "week_ending": pulse.week_ending.isoformat(),
        "generated_at": datetime.now().isoformat(),
        "word_count": pulse.word_count,
        "stats": {
            "total_reviews": len(raw_reviews),
            "clean_reviews_count": len(clean_reviews),
            "average_rating": avg_rating,
            "themes_count": len(clusters),
            "action_ideas_count": len(pulse.action_ideas),
            "word_count": pulse.word_count,
        },
        "top_themes": top_themes_data,
        "all_themes": all_themes_data,
        "user_quotes": pulse.user_quotes,
        "action_ideas": pulse.action_ideas,
        "markdown": md_output,
        "doc_url": doc_url or f"output/pulse_{today_iso}.md",
        "draft_id": draft_id or "local_stub",
    }

    # Save latest pulse JSON
    json_filepath = os.path.join("output", "latest_pulse.json")
    with open(json_filepath, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2)

    # Save reviews JSON for the verbatims feed
    reviews_data = [
        {
            "id": r.id,
            "rating": r.rating,
            "date": r.date.isoformat() if hasattr(r.date, "isoformat") else str(r.date),
            "text": r.text,
            "title": r.title,
        }
        for r in clean_reviews[:50]
    ]
    with open(os.path.join("output", "latest_reviews.json"), "w", encoding="utf-8") as f:
        json.dump(reviews_data, f, indent=2)

    log("complete", "done", "Agent run completed successfully!", result_data)
    return result_data


def run():
    """CLI Entrypoint"""
    run_pipeline()


if __name__ == "__main__":
    run()
