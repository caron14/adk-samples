"""Fetch simple financial summary using Yahoo Finance."""

from __future__ import annotations

import requests


SUMMARY_URL = (
    "https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
)


MODULES = ["earnings", "defaultKeyStatistics"]


def get_financial_summary(ticker: str) -> dict:
    """Retrieve earnings summary data from Yahoo Finance."""
    url = SUMMARY_URL.format(ticker=ticker)
    try:
        resp = requests.get(url, params={"modules": ",".join(MODULES)}, timeout=10)
    except Exception as exc:
        return {"status": "error", "error_message": str(exc)}
    if resp.status_code != 200:
        return {"status": "error", "error_message": f"HTTP {resp.status_code}"}
    data = resp.json()
    result = data.get("quoteSummary", {}).get("result")
    if not result:
        return {"status": "error", "error_message": "No summary data"}
    return {"status": "success", "summary": result[0]}
