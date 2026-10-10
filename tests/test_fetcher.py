import datetime
from unittest.mock import patch

from src.ingestion.fetcher import fetch_reviews


@patch("src.ingestion.fetcher.reviews")
def test_fetch_reviews(mock_reviews):
    mock_reviews.return_value = (
        [
            {"content": "Great app", "at": datetime.datetime.now(), "score": 5},
            {"content": "Bad app", "at": datetime.datetime.now(), "score": 1},
            {"content": "Great app", "at": datetime.datetime.now(), "score": 5} # duplicate text
        ],
        None
    )
    
    result = fetch_reviews("com.nextbillion.groww", lookback_weeks=10, max_count=10)
    assert len(result) == 2 # one duplicate dropped
    assert result[0].rating == 5
    assert result[1].rating == 1

@patch("src.ingestion.fetcher.reviews")
def test_fetch_reviews_network_error(mock_reviews):
    mock_reviews.side_effect = Exception("Network Error")
    result = fetch_reviews("com.nextbillion.groww")
    assert result == []
