"""Utilities to validate stock tickers using Yahoo Finance."""

from __future__ import annotations

import requests


YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"


def validate_ticker(ticker: str) -> dict:
    """Validate a ticker symbol via Yahoo Finance."""
    try:
        resp = requests.get(YAHOO_QUOTE_URL, params={"symbols": ticker}, timeout=10)
    except Exception as exc:
        return {"status": "error", "error_message": str(exc)}
    if resp.status_code != 200:
        return {"status": "error", "error_message": f"HTTP {resp.status_code}"}

    data = resp.json()
    results = data.get("quoteResponse", {}).get("result", [])
    if not results:
        return {"status": "error", "error_message": f"Ticker '{ticker}' not found"}
    return {"status": "success", "data": results[0]}
