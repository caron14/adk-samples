"""Retrieve news headlines using DuckDuckGo."""

from __future__ import annotations

import requests
from typing import List, Dict


DUCKDUCKGO_URL = "https://duckduckgo.com/"


def search_news(query: str, max_results: int = 5) -> dict:
    """Search DuckDuckGo news and return titles and snippets."""
    params = {
        "q": query,
        "format": "json",
        "no_redirect": 1,
        "no_html": 1,
        "skip_disambig": 1,
        "t": "adk-agent",
    }
    try:
        resp = requests.get(DUCKDUCKGO_URL, params=params, timeout=10)
    except Exception as exc:
        return {"status": "error", "error_message": str(exc)}
    if resp.status_code != 200:
        return {"status": "error", "error_message": f"HTTP {resp.status_code}"}
    data = resp.json()
    results: List[Dict[str, str]] = []
    for item in data.get("results", [])[:max_results]:
        results.append({
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "url": item.get("url"),
        })
    return {"status": "success", "articles": results}
