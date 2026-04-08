"""
Stress score fusion engine.
Combines psychometric assessment scores with NLP sentiment scores.
Formula: fused = 0.6 * psychometric + 0.4 * NLP
"""

PSYCHOMETRIC_WEIGHT = 0.6
NLP_WEIGHT = 0.4

SCORE_TIERS = {
    "minimal": (0.0, 2.0),
    "mild": (2.1, 4.5),
    "moderate": (4.6, 7.0),
    "moderately_severe": (7.1, 8.9),
    "severe": (9.0, 10.0),
}

TIER_BOUNDARIES = [2.0, 4.5, 7.0, 8.9]
YELLOW_FLAG_THRESHOLD = 0.5


def compute_fused_score(psychometric: float, nlp: float) -> float:
    """
    Compute fused stress score from psychometric and NLP components.
    Both inputs should be on 0-10 scale.
    """
    fused = PSYCHOMETRIC_WEIGHT * psychometric + NLP_WEIGHT * nlp
    return round(min(max(fused, 0.0), 10.0), 2)


def categorize_score(score: float) -> str:
    """Map a 0-10 score to a severity category."""
    for category, (low, high) in SCORE_TIERS.items():
        if low <= score <= high:
            return category
    return "severe" if score >= 9.0 else "minimal"


def check_yellow_flag(score: float) -> bool:
    """Check if score is within threshold of any tier boundary."""
    return any(abs(score - boundary) <= YELLOW_FLAG_THRESHOLD for boundary in TIER_BOUNDARIES)


def compute_full(psychometric: float, nlp: float) -> dict:
    """Compute fused score with category and yellow flag."""
    fused = compute_fused_score(psychometric, nlp)
    return {
        "psychometric_score": psychometric,
        "nlp_score": nlp,
        "fused_score": fused,
        "category": categorize_score(fused),
        "yellow_flag": check_yellow_flag(fused),
    }
