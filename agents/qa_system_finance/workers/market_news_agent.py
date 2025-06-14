"""
Market News Agent.

This module defines the MarketNewsAgent class, responsible for searching for
general financial market news for a given period using DuckDuckGo search.
"""
from duckduckgo_search import DDGS

class MarketNewsAgent:
    """
    Agent responsible for finding general financial market news.

    It uses DuckDuckGo search to find articles related to market trends, outlooks,
    or economic news for a specified period.
    """

    def get_market_news(self, year: str, month: str, period_description: str) -> list[dict]:
        """
        Searches for general financial market news for a given period.

        The query combines year, month, and a general period description to find
        broad market news, economic trends, or stock market outlooks.

        Args:
            year: The year of interest (e.g., "2023").
            month: The month of interest (e.g., "July", "10"). This can be part of
                   the period_description as well.
            period_description: A textual description of the period (e.g.,
                                "Q3 2023", "July 2023", "outlook for 2024").
                                This is the primary driver for the search period.

        Returns:
            A list of dictionaries, where each dictionary contains:
            - "title": The title of the news article.
            - "url": The URL of the news article.
            - "summary": A brief snippet or summary from the article.
            Returns an empty list if no relevant news is found or if an error
            occurs during the search.
        """
        # Construct a query for general market news.
        # Using period_description as the main time filter.
        # region='wt-wt' aims for worldwide results.
        query = (f"financial market news {period_description} OR "
                 f"stock market outlook {period_description} OR "
                 f"economic trends {period_description}")

        results_list = []

        try:
            # Perform search using DuckDuckGo
            search_results_generator = DDGS().text(query, max_results=5, region='wt-wt')

            if search_results_generator:
                for r in search_results_generator:
                    results_list.append({
                        "title": r.get('title', 'N/A'),
                        "url": r.get('href', '#'),
                        "summary": r.get('body', 'N/A')
                    })
            return results_list
        except Exception as e:
            # Log error for debugging
            print(f"Error searching for market news for {period_description}: {e}")
            # Return empty list on error
            return []

if __name__ == '__main__':
    # Example usage for testing the agent directly
    agent = MarketNewsAgent()
    print("--- Testing MarketNewsAgent ---")

    # Test Case 1: Specific recent period
    print("\nTest Case 1: Period 'July 2023'")
    market_news1 = agent.get_market_news("2023", "July", "July 2023")
    print(f"Found {len(market_news1)} market news articles.")
    if market_news1:
        for i, article in enumerate(market_news1):
            print(f"  Article {i+1}: {article['title']} ({article['url']})")
    else:
        print("  No market news found for July 2023 (or an error occurred).")

    # Test Case 2: Broader outlook query
    print("\nTest Case 2: Period 'outlook for 2024'")
    # Month is not strictly necessary here if 'period_description' is comprehensive.
    market_news2 = agent.get_market_news("2024", "", "outlook for 2024")
    print(f"Found {len(market_news2)} market news articles.")
    if not market_news2:
        print("  No market news found for 'outlook for 2024' (or an error occurred).")

    # Test Case 3: Specific quarter
    print("\nTest Case 3: Period 'Q1 2023'")
    market_news3 = agent.get_market_news("2023", "Q1", "Q1 2023")
    print(f"Found {len(market_news3)} market news articles.")
    if not market_news3:
        print("  No market news found for Q1 2023 (or an error occurred).")

    print("\n--- MarketNewsAgent Test Complete ---")
