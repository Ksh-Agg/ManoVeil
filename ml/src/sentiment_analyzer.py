"""
VADER-based sentiment analyzer for ManoVeil.
Used for NLP scoring in the stress fusion pipeline.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Module-level singleton
_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of text using VADER.
    Returns dict with neg, neu, pos, compound scores.
    compound ranges from -1 (most negative) to +1 (most positive).
    """
    return _analyzer.polarity_scores(text)


def get_compound_score(text: str) -> float:
    """Get just the compound sentiment score (-1 to +1)."""
    return _analyzer.polarity_scores(text)["compound"]


def sentiment_to_stress(compound: float) -> float:
    """
    Convert VADER compound score to stress scale (0-10).
    compound -1 (very negative) → stress 10
    compound +1 (very positive) → stress 0
    """
    return round((1 - compound) * 5, 2)


def batch_analyze(texts: list[str]) -> list[dict]:
    """Analyze sentiment for a batch of texts."""
    return [analyze_sentiment(text) for text in texts]
