"""Simple sentiment analysis utility."""

from __future__ import annotations

from typing import Dict

POSITIVE_WORDS = {"good", "positive", "growth", "gain", "strong", "improve"}
NEGATIVE_WORDS = {"bad", "negative", "decline", "loss", "weak", "drop"}


def analyze_sentiment(text: str) -> dict:
    """Very naive sentiment analysis based on word counts."""
    text_lower = text.lower()
    score = 0
    for word in POSITIVE_WORDS:
        if word in text_lower:
            score += 1
    for word in NEGATIVE_WORDS:
        if word in text_lower:
            score -= 1
    if score > 0:
        sentiment = "positive"
    elif score < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return {"status": "success", "sentiment": sentiment, "score": score}
