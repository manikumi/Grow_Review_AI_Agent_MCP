import re

from src.ingestion.models import Review


class CleanReview(Review):
    """
    Same as Review but guaranteed to have PII scrubbed from text.
    """

# Common patterns for PII in Indian context
PATTERNS = {
    "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "PHONE": r"(?:\+91[-.\s]?|91[-.\s]?)?[6-9]\d{9}\b",  # Indian mobile numbers
    "UPI_ID": r"[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}",
    "DEVICE_MODEL": r"\b(SM-[A-Z0-9]+|iPhone\s*\d+|Pixel\s*\d+|Redmi\s*Note\s*\d+|OnePlus\s*\d+)\b"
}

def scrub(reviews: list[Review]) -> list[CleanReview]:
    """
    Strips PII from review text before LLM processing.
    Drops reviews where >50% of the text is redacted.
    """
    clean_reviews = []
    
    for r in reviews:
        original_text = r.text
        if not original_text:
            continue
            
        scrubbed_text = original_text
        
        # Apply redactions
        for p_name, pattern in PATTERNS.items():
            scrubbed_text = re.sub(pattern, "[REDACTED]", scrubbed_text, flags=re.IGNORECASE)
            
        # Calculate redaction ratio
        original_len = len(original_text)
        if original_len == 0:
            continue
            
        redacted_count = scrubbed_text.count("[REDACTED]")
        # Approximate length of redacted content (10 chars per REDACTED token to be safe)
        redacted_approx_len = redacted_count * 10 
        
        if redacted_approx_len > (original_len * 0.5):
            # Drop review if more than 50% of it is considered redacted
            continue
            
        clean_r = CleanReview(
            id=r.id,
            rating=r.rating,
            date=r.date,
            text=scrubbed_text,
            title=r.title
        )
        clean_reviews.append(clean_r)
        
    return clean_reviews

if __name__ == "__main__":
    # Smoke test for scrubber
    import datetime
    sample = [
        Review(id="1", rating=1, date=datetime.date.today(), text="Call me at +91 9876543210 or email test@example.com my upi is test@ybl. I have a SM-G998B"),
        Review(id="2", rating=5, date=datetime.date.today(), text="Good app, love it!"),
        Review(id="3", rating=1, date=datetime.date.today(), text="test@example.com +919876543210 test2@okhdfcbank +919876543211") # Highly redacted
    ]
    
    cleaned = scrub(sample)
    print(f"Original count: {len(sample)}, Cleaned count: {len(cleaned)}")
    for c in cleaned:
        print(f"[{c.id}] {c.text}")
