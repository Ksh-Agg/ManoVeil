"""
Crisis detection module.
Detects crisis indicators from text content and stress scores.
"""

CRISIS_KEYWORDS = [
    "kill myself", "suicide", "suicidal", "end my life", "want to die",
    "no reason to live", "better off dead", "self harm", "self-harm",
    "cut myself", "cutting", "hurt myself", "overdose", "jump off",
    "hang myself", "not worth living", "can't go on", "ending it",
    "goodbye forever", "final goodbye", "last message",
]

SCORE_CRISIS_THRESHOLD = 9.0


def check_text_crisis(text: str) -> dict:
    """
    Check text for crisis indicators using keyword matching.
    Returns detection result with matched keywords.
    """
    text_lower = text.lower()
    matched = [kw for kw in CRISIS_KEYWORDS if kw in text_lower]

    return {
        "is_crisis": len(matched) > 0,
        "matched_keywords": matched,
        "confidence": min(len(matched) / 3, 1.0) if matched else 0.0,
    }


def check_score_crisis(score: float) -> dict:
    """
    Check if a stress score indicates crisis level.
    """
    return {
        "is_crisis": score >= SCORE_CRISIS_THRESHOLD,
        "score": score,
        "threshold": SCORE_CRISIS_THRESHOLD,
    }


def detect_crisis(text: str | None = None, score: float | None = None) -> dict:
    """
    Combined crisis detection from text and/or score.
    Returns overall crisis assessment.
    """
    text_result = check_text_crisis(text) if text else {"is_crisis": False, "matched_keywords": [], "confidence": 0.0}
    score_result = check_score_crisis(score) if score is not None else {"is_crisis": False}

    is_crisis = text_result["is_crisis"] or score_result["is_crisis"]

    severity = "none"
    if is_crisis:
        if text_result["is_crisis"] and score_result.get("is_crisis"):
            severity = "sos"
        elif text_result.get("confidence", 0) > 0.5:
            severity = "red"
        elif text_result["is_crisis"]:
            severity = "orange"
        else:
            severity = "red"

    return {
        "is_crisis": is_crisis,
        "severity": severity,
        "text_crisis": text_result,
        "score_crisis": score_result,
        "action": "immediate_intervention" if severity in ("sos", "red") else "monitor" if severity == "orange" else "none",
    }
