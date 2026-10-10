import datetime

from src.ingestion.models import Review
from src.processing.scrubber import scrub


def test_scrub_pii_patterns():
    reviews = [
        Review(
            id="1", 
            rating=5, 
            date=datetime.date(2026, 1, 1), 
            text="Call me at +91 9876543210 or email test@example.com my upi is test@ybl. I have a SM-G998B"
        )
    ]
    cleaned = scrub(reviews)
    assert len(cleaned) == 1
    assert "9876543210" not in cleaned[0].text
    assert "test@example.com" not in cleaned[0].text
    assert "test@ybl" not in cleaned[0].text
    assert "SM-G998B" not in cleaned[0].text
    assert "[REDACTED]" in cleaned[0].text

def test_scrub_high_redaction_drop():
    reviews = [
        Review(
            id="2", 
            rating=1, 
            date=datetime.date(2026, 1, 1), 
            text="test@example.com +919876543210 test2@okhdfcbank +919876543211"
        )
    ]
    cleaned = scrub(reviews)
    assert len(cleaned) == 0
