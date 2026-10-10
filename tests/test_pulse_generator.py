import datetime
import json
from unittest.mock import MagicMock, patch

from src.processing.clusterer import ThemeCluster
from src.processing.pulse_generator import generate_pulse, render_pulse
from src.processing.scrubber import CleanReview


@patch("src.processing.pulse_generator.Groq")
def test_generate_pulse(mock_groq_class):
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(["Idea 1", "Idea 2", "Idea 3"])
    mock_client.chat.completions.create.return_value = mock_response
    
    clusters = [
        ThemeCluster(name="Theme1", review_ids=["1"], count=10, summary="t1"),
        ThemeCluster(name="Theme2", review_ids=["2"], count=5, summary="t2"),
        ThemeCluster(name="Theme3", review_ids=["3"], count=1, summary="t3")
    ]
    reviews = [
        CleanReview(id="1", rating=5, date=datetime.date.today(), text="review 1"),
        CleanReview(id="2", rating=5, date=datetime.date.today(), text="review 2"),
        CleanReview(id="3", rating=5, date=datetime.date.today(), text="review 3")
    ]
    
    pulse = generate_pulse(clusters, reviews)
    assert len(pulse.top_themes) == 3
    assert len(pulse.user_quotes) == 3
    assert len(pulse.action_ideas) == 3

def test_render_pulse_truncation():
    from src.processing.pulse_generator import WeeklyPulse
    pulse = WeeklyPulse(
        week_ending=datetime.date.today(),
        top_themes=[],
        user_quotes=[],
        action_ideas=["word " * 300]
    )
    md = render_pulse(pulse)
    assert pulse.word_count == 250
    assert "... (truncated" in md
