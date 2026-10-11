import datetime
import json
from unittest.mock import patch

from src.ingestion.fetcher import (
    fetch_reviews,
    has_emoji,
    is_english,
    is_valid_review,
    save_reviews_jsonl,
)
from src.ingestion.models import Review


@patch("src.ingestion.fetcher.reviews")
def test_fetch_reviews(mock_reviews):
    long_text_1 = "This application is exceptionally useful and smooth for managing my mutual funds daily"
    long_text_2 = "Customer support never replied to my query regarding redemption of units from the folio"
    mock_reviews.return_value = (
        [
            {"content": long_text_1, "at": datetime.datetime.now(), "score": 5},
            {"content": long_text_2, "at": datetime.datetime.now(), "score": 1},
            {"content": long_text_1, "at": datetime.datetime.now(), "score": 5},  # duplicate text
        ],
        None
    )

    result = fetch_reviews("com.nextbillion.groww", lookback_weeks=10, max_count=10)
    assert len(result) == 2  # one duplicate dropped
    assert result[0].rating == 5
    assert result[1].rating == 1


def test_is_valid_review_word_count():
    # <= 8 words should fail
    short_text = "Good app very nice trading platform today"  # 7 words
    assert not is_valid_review(short_text, min_words=8)

    # > 8 words should pass
    long_text = "This application is exceptionally good and easy to use for regular investing"  # 11 words
    assert is_valid_review(long_text, min_words=8)


def test_is_valid_review_emojis():
    assert has_emoji("Good app 👍")
    assert not is_valid_review("Good trading application for stocks and mutual fund investors 👍", filter_emojis=True)


def test_is_valid_review_non_english():
    # Non-Latin script (Hindi)
    hindi_text = "यह बहुत अच्छा ऐप है निवेश करने के लिए धन्यवाद"
    assert not is_valid_review(hindi_text, filter_non_english=True)

    # Hinglish text with multiple Hindi stopwords
    hinglish_text = "bahut bekar app hai paise kat liye or refund nahi diya groww ne"
    assert not is_valid_review(hinglish_text, filter_non_english=True)


def test_save_reviews_jsonl(tmp_path):
    target_file = tmp_path / "test_reviews.jsonl"
    reviews_list = [
        Review(
            id="hash1",
            rating=5,
            date=datetime.date(2026, 1, 1),
            text="This is a fantastic application for trading in India with simple UI"
        )
    ]
    save_reviews_jsonl(reviews_list, str(target_file))

    assert target_file.exists()
    lines = target_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["id"] == "hash1"
    assert data["rating"] == 5
    assert data["text"] == "This is a fantastic application for trading in India with simple UI"


@patch("src.ingestion.fetcher.reviews")
def test_fetch_reviews_network_error(mock_reviews):
    mock_reviews.side_effect = Exception("Network Error")
    result = fetch_reviews("com.nextbillion.groww")
    assert result == []

