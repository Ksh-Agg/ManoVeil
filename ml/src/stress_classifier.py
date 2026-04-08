"""
Stress score classifier.
Provides category classification and risk assessment from stress scores.
"""

from .fusion_engine import SCORE_TIERS, categorize_score, check_yellow_flag


def classify(score: float) -> dict:
    """
    Classify a stress score into category with risk metadata.
    """
    category = categorize_score(score)
    yellow_flag = check_yellow_flag(score)

    risk_levels = {
        "minimal": "low",
        "mild": "low",
        "moderate": "moderate",
        "moderately_severe": "high",
        "severe": "critical",
    }

    return {
        "score": score,
        "category": category,
        "risk_level": risk_levels.get(category, "unknown"),
        "yellow_flag": yellow_flag,
        "needs_intervention": category in ("moderate", "moderately_severe", "severe"),
        "needs_crisis_check": category in ("moderately_severe", "severe"),
    }


def detect_trend(scores: list[float], window: int = 5) -> str:
    """
    Detect trend in recent scores.
    Returns: 'improving', 'declining', or 'stable'
    """
    if len(scores) < 2:
        return "stable"

    recent = scores[-window:]
    if len(recent) < 2:
        return "stable"

    avg_first_half = sum(recent[: len(recent) // 2]) / (len(recent) // 2)
    avg_second_half = sum(recent[len(recent) // 2 :]) / (len(recent) - len(recent) // 2)

    diff = avg_second_half - avg_first_half
    if diff < -0.5:
        return "improving"
    elif diff > 0.5:
        return "declining"
    return "stable"
