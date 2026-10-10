import hashlib
from datetime import date, datetime, timedelta

from google_play_scraper import Sort, reviews
from rich.console import Console

from src.ingestion.models import Review

console = Console()


def fetch_reviews(app_id: str, lookback_weeks: int = 10, max_count: int = 500) -> list[Review]:
    """
    Fetches the latest reviews for a given Google Play app.
    Normalises them into the Review model, stripping PII like reviewer names.
    Deduplicates based on the SHA-256 hash of the review text.
    """
    console.print(f"[bold blue]Fetching up to {max_count} reviews for {app_id} (lookback: {lookback_weeks} weeks)...[/bold blue]")
    
    threshold_date: date = (datetime.now() - timedelta(weeks=lookback_weeks)).date()
    
    try:
        # We use Sort.NEWEST to get the latest reviews
        result, _ = reviews(
            app_id,
            lang="en",
            country="in",
            sort=Sort.NEWEST,
            count=max_count
        )
    except Exception as e:
        console.print(f"[bold red]Failed to fetch reviews: {e}[/bold red]")
        return []
        
    if not result:
        console.print("[bold yellow]No reviews returned by the scraper.[/bold yellow]")
        return []
        
    fetched_reviews = []
    seen_ids = set()
    
    for r in result:
        # Extract fields
        text = r.get("content", "")
        if not text:
            continue
            
        review_date = r.get("at")
        if isinstance(review_date, datetime):
            review_date = review_date.date()
            
        if review_date and review_date < threshold_date:
            # Since it's sorted by newest, we could technically break early,
            # but we'll just continue/break depending on how the scraper returns it.
            # Let's break early since it's strictly ordered.
            continue
            
        # Deduplicate using SHA-256 of the text
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        
        if text_hash in seen_ids:
            continue
            
        seen_ids.add(text_hash)
        
        review_obj = Review(
            id=text_hash,
            rating=r.get("score", 0),
            date=review_date,
            text=text,
            # Play store reviews typically don't have separate titles in this API, 
            # but we can set it to None.
            title=None
        )
        
        fetched_reviews.append(review_obj)
        
    console.print(f"[bold green]Successfully ingested {len(fetched_reviews)} reviews after filtering and deduplication.[/bold green]")
    return fetched_reviews


if __name__ == "__main__":
    from src.utils.config import GROWW_APP_ID, REVIEW_LOOKBACK_WEEKS, REVIEW_MAX_COUNT
    
    console.print("[bold yellow]Running Manual Smoke Test for Review Ingestion...[/bold yellow]")
    
    sample_reviews = fetch_reviews(
        app_id=GROWW_APP_ID,
        lookback_weeks=REVIEW_LOOKBACK_WEEKS,
        max_count=REVIEW_MAX_COUNT
    )
    
    console.print("\n[bold]Top 5 reviews ingested:[/bold]")
    for idx, rev in enumerate(sample_reviews[:5]):
        console.print(f"  {idx+1}. [bold cyan]{rev.date}[/bold cyan] | Rating: [yellow]{rev.rating}/5[/yellow]")
        console.print(f"     ID: {rev.id[:8]}...")
        console.print(f"     Text: {rev.text[:100]}...\n")
