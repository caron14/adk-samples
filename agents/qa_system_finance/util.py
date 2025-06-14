import json
from datetime import datetime
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from typing import Dict, List

import yfinance as yf

POSITIVE_WORDS = {
    "gain",
    "growth",
    "positive",
    "surge",
    "beat",
    "up",
    "profit",
}
NEGATIVE_WORDS = {
    "loss",
    "drop",
    "negative",
    "down",
    "miss",
    "decline",
}

MAX_ARTICLES = 10


def validate_ticker(ticker: str) -> Dict[str, str]:
    """Validate ticker symbol using yfinance."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        # yfinance returns an empty dict for invalid tickers
        if info and info.get("regularMarketPrice") is not None:
            return {"status": "success", "ticker": ticker.upper()}
        return {
            "status": "error",
            "error_message": f"Ticker '{ticker.upper()}' not found.",
        }
    except Exception as err:
        return {"status": "error", "error_message": str(err)}


def search_news(query: str, start: datetime, end: datetime) -> Dict[str, List[Dict[str, str]]]:
    """Search news on DuckDuckGo between start and end dates."""
    date_range = f"{start.strftime('%Y-%m-%d')}..{end.strftime('%Y-%m-%d')}"
    q = quote_plus(f"{query} {date_range}")
    url = f"https://duckduckgo.com/?q={q}&iar=news&ia=news&format=json"
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req) as resp:
            data = json.load(resp)
        articles = []
        for item in data.get("results", []) or data.get("RelatedTopics", []):
            title = item.get("title") or item.get("Text")
            link = item.get("url") or item.get("FirstURL")
            snippet = item.get("snippet") or ""
            if title and link:
                articles.append(
                    {"title": title, "url": link, "snippet": snippet}
                )
            if len(articles) >= MAX_ARTICLES:
                break
        return {"status": "success", "articles": articles}
    except Exception as err:  # pragma: no cover - network
        return {"status": "error", "error_message": str(err)}


def summarize_financials(ticker: str) -> Dict[str, Dict[str, str]]:
    """Fetch simple earnings summary from Yahoo Finance."""
    url = (
        "https://query1.finance.yahoo.com/v10/finance/quoteSummary/"
        + quote_plus(ticker)
        + "?modules=earnings"
    )
    try:
        with urlopen(url) as resp:
            data = json.load(resp)
        summary = data.get("quoteSummary", {}).get("result", [{}])[0]
        return {"status": "success", "summary": summary}
    except Exception as err:  # pragma: no cover - network
        return {"status": "error", "error_message": str(err)}


def analyze_sentiment(text: str) -> Dict[str, str]:
    """Very small sentiment analyzer based on word lists."""
    lower = text.lower()
    score = 0
    for w in POSITIVE_WORDS:
        if w in lower:
            score += 1
    for w in NEGATIVE_WORDS:
        if w in lower:
            score -= 1
    if score > 0:
        sentiment = "positive"
    elif score < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return {"status": "success", "sentiment": sentiment, "score": score}


if __name__ == "__main__":
    pass
