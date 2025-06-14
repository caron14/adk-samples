"""
Company News Agent.

This module defines the CompanyNewsAgent class, responsible for searching for
news articles specific to a given company over a certain period, using the
DuckDuckGo search engine.
"""
from duckduckgo_search import DDGS

class CompanyNewsAgent:
    """
    Agent responsible for finding company-specific news articles.

    It uses DuckDuckGo search to find news related to a company name or
    ticker symbol for a described period.
    """

    def get_company_news(self, company_name: str, ticker_symbol: str, period_description: str) -> list[dict]:
        """
        Searches for company-specific news during a given period.

        The query is constructed to find news articles for the company, attempting
        to exclude financial reports for more focused news results.

        Args:
            company_name: The name of the company (e.g., "NVIDIA").
            ticker_symbol: The stock ticker symbol (e.g., "NVDA").
            period_description: A textual description of the period for which news
                                is sought (e.g., "past week", "July 2023",
                                "the week of 2023-10-16 to 2023-10-20").

        Returns:
            A list of dictionaries, where each dictionary contains:
            - "title": The title of the news article.
            - "url": The URL of the news article.
            - "summary": A brief snippet or summary from the article.
            Returns an empty list if no relevant news is found or if an error
            occurs during the search.
        """
        # Construct a query to find company news, trying to filter out routine financial reports
        # The effectiveness of "-<term>" depends on search engine behavior.
        query = (f"{company_name} OR {ticker_symbol} company news {period_description} "
                 f"-\"earnings report\" -\"financial results\" -\"annual report\"")

        results_list = []

        try:
            # Perform search using DuckDuckGo
            search_results_generator = DDGS().text(query, max_results=5)

            if search_results_generator:
                for r in search_results_generator:
                    results_list.append({
                        "title": r.get('title', 'N/A'),
                        "url": r.get('href', '#'),
                        "summary": r.get('body', 'N/A')
                    })
            return results_list
        except Exception as e:
            # Log the error for debugging
            print(f"Error searching for company news for {company_name} ({period_description}): {e}")
            # Return an empty list to ensure graceful failure
            return []

if __name__ == '__main__':
    # Example usage for testing the agent directly
    agent = CompanyNewsAgent()
    print("--- Testing CompanyNewsAgent ---")

    # Test Case 1: Well-known company, recent general period
    # Note: "last week" is dynamic; results will vary based on execution time.
    print("\nTest Case 1: Apple Inc. (AAPL), Period: 'the last 7 days'")
    news1 = agent.get_company_news("Apple Inc.", "AAPL", "the last 7 days")
    print(f"Found {len(news1)} news articles.")
    if news1:
        for i, article in enumerate(news1):
            print(f"  Article {i+1}: {article['title']} ({article['url']})")
    else:
        print("  No news found for Apple in the last 7 days (or an error occurred).")

    # Test Case 2: Specific company and a defined past period
    print("\nTest Case 2: Microsoft (MSFT), Period: 'June 2023'")
    news2 = agent.get_company_news("Microsoft", "MSFT", "June 2023")
    print(f"Found {len(news2)} news articles.")
    if not news2:
        print("  No news found for Microsoft in June 2023 (or an error occurred).")

    # Test Case 3: Using a more specific weekly description
    print("\nTest Case 3: Tesla (TSLA), Period: 'the week of 2023-10-16 to 2023-10-20'")
    news3 = agent.get_company_news("Tesla", "TSLA", "the week of 2023-10-16 to 2023-10-20")
    print(f"Found {len(news3)} news articles.")
    if not news3:
        print("  No news found for Tesla for that specific week (or an error occurred).")

    print("\n--- CompanyNewsAgent Test Complete ---")
