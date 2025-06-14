from adk.tools import tool
from duckduckgo_search import DDGS
from datetime import datetime, timedelta

@tool
def search_news_for_week(ticker_symbol: str, week_monday_str: str) -> dict:
    """
    Searches for news articles for a given stock ticker and a specific week.
    'week_monday_str' should be a date string 'YYYY-MM-DD' representing the Monday of the target week.
    Returns a dictionary containing a list of news items or an error message.
    """
    try:
        # Determine the start and end dates for the search query
        start_date = datetime.strptime(week_monday_str, "%Y-%m-%d")
        end_date = start_date + timedelta(days=6)

        query = f"{ticker_symbol} stock news {start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"

        results = []
        # Using DDGS context manager for cleaner resource handling
        with DDGS() as ddgs:
            # ddgs.news returns a generator
            for r in ddgs.news(
                keywords=query,
                region='wt-wt', # World-wide
                safesearch='moderate',
                timelimit='w', # 'd' (day), 'w' (week), 'm' (month), 'y' (year) - using 'w' and specific date range in query
                max_results=10 # Limiting results
            ):
                results.append({
                    "title": r.get("title"),
                    "body": r.get("body"), # Snippet/summary
                    "url": r.get("url"),
                    "date": r.get("date") # Publication date string
                })

        if not results:
            return {"news_items": [], "message": f"No news found for {ticker_symbol} for the week of {week_monday_str}."}

        return {"news_items": results}

    except Exception as e:
        return {"error": f"Error searching news for {ticker_symbol}: {str(e)}"}
