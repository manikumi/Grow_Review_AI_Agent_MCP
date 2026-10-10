import datetime
import json
from unittest.mock import MagicMock, patch

from src.processing.clusterer import cluster_themes
from src.processing.scrubber import CleanReview


@patch("src.processing.clusterer.Groq")
def test_cluster_themes_success(mock_groq_class):
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "clusters": [
            {"name": "Theme1", "review_ids": ["1", "2"], "summary": "t1"},
            {"name": "Theme2", "review_ids": ["3"], "summary": "t2"},
            {"name": "Theme3", "review_ids": ["4"], "summary": "t3"},
            {"name": "Theme4", "review_ids": ["5"], "summary": "t4"},
            {"name": "Theme5", "review_ids": ["6"], "summary": "t5"},
            {"name": "Theme6", "review_ids": ["7"], "summary": "t6"}
        ]
    })
    mock_client.chat.completions.create.return_value = mock_response

    reviews = [CleanReview(id=str(i), rating=5, date=datetime.date.today(), text=f"text {i}") for i in range(1, 8)]
    
    clusters = cluster_themes(reviews)
    assert len(clusters) == 5
    assert clusters[-1].name == "Other"

@patch("src.processing.clusterer.Groq")
def test_cluster_themes_json_retry(mock_groq_class):
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    mock_response_bad = MagicMock()
    mock_response_bad.choices = [MagicMock()]
    mock_response_bad.choices[0].message.content = "Not JSON"
    
    mock_response_good = MagicMock()
    mock_response_good.choices = [MagicMock()]
    mock_response_good.choices[0].message.content = json.dumps({
        "clusters": [{"name": "Theme1", "review_ids": ["1"], "summary": "t1"}]
    })
    
    mock_client.chat.completions.create.side_effect = [mock_response_bad, mock_response_good]
    
    reviews = [CleanReview(id="1", rating=5, date=datetime.date.today(), text="text")]
    clusters = cluster_themes(reviews)
    
    assert len(clusters) == 1
    assert mock_client.chat.completions.create.call_count == 2

@patch("src.processing.clusterer.Groq")
def test_cluster_themes_token_budget(mock_groq_class):
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({"clusters": []})
    mock_client.chat.completions.create.return_value = mock_response
    
    long_text = "a" * 17000
    reviews = [CleanReview(id="1", rating=5, date=datetime.date.today(), text=long_text)]
    
    clusters = cluster_themes(reviews)
    assert len(clusters) == 0
