import hashlib
import json
import re
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from google_play_scraper import Sort, reviews
from langdetect import DetectorFactory, detect
from rich.console import Console

from src.ingestion.models import Review

DetectorFactory.seed = 0
console = Console()

HINDI_STOPWORDS = {
    "karo", "karega", "karna", "karte", "hai", "hain", "nahi", "nhi", "mat",
    "hoga", "hogi", "mera", "meri", "mere", "mujhe", "mujhko", "bhi", "tha",
    "thi", "the", "rha", "rhi", "rahe", "wala", "wali", "wale", "paise",
    "paisa", "bekar", "aaya", "aayi", "diya", "diye", "hum", "sab", "apka",
    "apki", "apke", "bata", "kuch", "bahut", "bohot", "acha", "accha", "jyada",
    "jada", "lekin", "lakin", "aur", "ya", "ye", "yeh", "wo", "woh", "sirf",
    "bhai", "taki", "phle", "pehle", "baar", "bar", "dega", "degi", "dena",
    "liya", "liye", "kya", "kyu", "kyun", "kyuki", "jab", "tab", "ab", "se",
    "ko", "me", "mai", "mein", "par", "pe", "ka", "ki", "ke"
}


def has_emoji(text: str) -> bool:
    """Returns True if the text contains any emoji characters."""
    for ch in text:
        cat = unicodedata.category(ch)
        if cat in ("So",) or 0x1F300 <= ord(ch) <= 0x1FAFF or 0x2600 <= ord(ch) <= 0x27BF:
            return True
    return False


def is_english(text: str) -> bool:
    """
    Returns True if the review text is in English.
    Rejects non-Latin scripts, Hinglish, and other languages detected via langdetect.
    """
    # Reject non-Latin characters (Devanagari, Tamil, etc.)
    for ch in text:
        if ord(ch) > 0x024F:
            if not ch.isspace() and unicodedata.category(ch)[0] in ("L", "M"):
                return False

    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    # Reject Hinglish by checking Romanized Hindi stopwords
    hindi_count = sum(1 for w in words if w in HINDI_STOPWORDS)
    if hindi_count >= 2:
        return False

    try:
        return detect(text) == "en"
    except Exception:
        return False


def is_valid_review(
    text: str,
    min_words: int = 8,
    filter_emojis: bool = True,
    filter_non_english: bool = True
) -> bool:
    """
    Validates a review text based on:
    1. Word count > min_words (more than 8 words)
    2. Exclusion of emoji reviews
    3. Exclusion of non-English / Hinglish reviews
    """
    if not text:
        return False

    # Check for emojis
    if filter_emojis and has_emoji(text):
        return False

    # Word count: must be > min_words
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text)
    if len(words) <= min_words:
        return False

    # Language check
    if filter_non_english and not is_english(text):
        return False

    return True


def save_reviews_jsonl(reviews_list: list[Review], file_path: str = "reviews.jsonl") -> str:
    """
    Writes a list of Review objects to a JSON Lines (.jsonl) file.
    """
    path = Path(file_path)
    with open(path, "w", encoding="utf-8") as f:
        for rev in reviews_list:
            f.write(rev.model_dump_json() + "\n")
    console.print(f"[bold green]Saved {len(reviews_list)} reviews to {path.resolve()}[/bold green]")
    return str(path.resolve())


def fetch_reviews(
    app_id: str,
    lookback_weeks: int = 10,
    max_count: int = 500,
    min_words: int = 8,
    filter_emojis: bool = True,
    filter_non_english: bool = True
) -> list[Review]:
    """
    Fetches latest reviews for a given Google Play app.
    Normalises them into the Review model, stripping PII like reviewer names.
    Applies filters:
      - Reviews with more than min_words (default > 8 words)
      - Drops emoji reviews
      - Drops other languages apart from English
    Deduplicates based on the SHA-256 hash of the review text.
    """
    console.print(f"[bold blue]Fetching up to {max_count} reviews for {app_id} (lookback: {lookback_weeks} weeks)...[/bold blue]")

    threshold_date: date = (datetime.now() - timedelta(weeks=lookback_weeks)).date()

    try:
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
        text = r.get("content", "").strip()
        if not text:
            continue

        review_date = r.get("at")
        if isinstance(review_date, datetime):
            review_date = review_date.date()

        if review_date and review_date < threshold_date:
            continue

        # Apply filtering (> 8 words, no emojis, english only)
        if not is_valid_review(
            text,
            min_words=min_words,
            filter_emojis=filter_emojis,
            filter_non_english=filter_non_english
        ):
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
            title=None
        )

        fetched_reviews.append(review_obj)

    console.print(f"[bold green]Successfully ingested {len(fetched_reviews)} reviews after filtering and deduplication.[/bold green]")
    return fetched_reviews


if __name__ == "__main__":
    from src.utils.config import GROWW_APP_ID, REVIEW_LOOKBACK_WEEKS, REVIEW_MAX_COUNT

    console.print("[bold yellow]Running Review Ingestion with Phase 2 Filters...[/bold yellow]")

    ingested_reviews = fetch_reviews(
        app_id=GROWW_APP_ID,
        lookback_weeks=REVIEW_LOOKBACK_WEEKS,
        max_count=REVIEW_MAX_COUNT,
        min_words=8,
        filter_emojis=True,
        filter_non_english=True
    )

    save_reviews_jsonl(ingested_reviews, "reviews.jsonl")

    console.print(f"\n[bold]Total reviews kept and saved: {len(ingested_reviews)}[/bold]")
    console.print("\n[bold]Top 5 reviews ingested:[/bold]")
    for idx, rev in enumerate(ingested_reviews[:5]):
        console.print(f"  {idx+1}. [bold cyan]{rev.date}[/bold cyan] | Rating: [yellow]{rev.rating}/5[/yellow]")
        console.print(f"     ID: {rev.id[:8]}...")
        console.print(f"     Text: {rev.text[:100]}...\n")
