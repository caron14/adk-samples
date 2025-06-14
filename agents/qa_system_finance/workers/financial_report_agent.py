"""
Financial Report Agent.

This module defines the FinancialReportAgent class, which is responsible for
searching for financial reports (like annual or earnings reports) for a given
company and year using the DuckDuckGo search engine.
"""
from duckduckgo_search import DDGS

class FinancialReportAgent:
    """
    Agent responsible for finding links to financial reports.

    It uses DuckDuckGo search to find relevant documents based on company name,
    ticker symbol, and year.
    """

    def get_financial_reports(self, company_name: str, ticker_symbol: str, year: str) -> list[dict]:
        """
        Searches for financial reports of a company for a specific year.

        Constructs a search query using the company name, ticker symbol, and year
        to find relevant financial or earnings reports.

        Args:
            company_name: The name of the company (e.g., "Apple Inc.").
            ticker_symbol: The stock ticker symbol of the company (e.g., "AAPL").
            year: The year for which financial reports are sought (e.g., "2022").

        Returns:
            A list of dictionaries, where each dictionary contains:
            - "title": The title of the search result.
            - "url": The URL of the search result.
            - "summary": A brief snippet or summary from the search result.
            Returns an empty list if no relevant results are found or if an error
            occurs during the search.
        """
        # Construct a comprehensive query to find financial reports
        query = (f"{company_name} OR {ticker_symbol} financial results {year} OR "
                 f"earnings report {year} OR annual report {year} investor relations {year}")

        results_list = []

        try:
            # Perform the search using DuckDuckGo
            # DDGS().text() returns a generator of search results.
            # max_results limits the number of results returned by the search.
            search_results_generator = DDGS().text(query, max_results=5)

            if search_results_generator:
                for r in search_results_generator:
                    # Append a dictionary of relevant information for each result
                    results_list.append({
                        "title": r.get('title', 'N/A'),  # Title of the page
                        "url": r.get('href', '#'),      # URL of the page
                        "summary": r.get('body', 'N/A') # Snippet/summary from the page
                    })
            return results_list
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error searching for financial reports for {company_name} ({year}): {e}")
            # Return an empty list in case of any error to ensure graceful failure
            return []

if __name__ == '__main__':
    # Example usage for testing the agent directly
    agent = FinancialReportAgent()
    print("--- Testing FinancialReportAgent ---")

    # Test Case 1: Well-known company and recent year
    print("\nTest Case 1: Apple Inc. (AAPL), Year 2022")
    reports1 = agent.get_financial_reports("Apple Inc.", "AAPL", "2022")
    print(f"Found {len(reports1)} reports.")
    if reports1:
        for i, report in enumerate(reports1):
            print(f"  Report {i+1}:")
            print(f"    Title: {report['title']}")
            print(f"    URL: {report['url']}")
            # print(f"    Summary: {report['summary'][:150]}...") # Print a short part of summary
    else:
        print("  No reports found or an error occurred for Test Case 1.")
    # It's hard to assert content here as search results are dynamic.
    # The main check is if it returns a list, possibly empty, without crashing.

    # Test Case 2: Another company
    print("\nTest Case 2: Microsoft (MSFT), Year 2023")
    reports2 = agent.get_financial_reports("Microsoft", "MSFT", "2023")
    print(f"Found {len(reports2)} reports.")
    if not reports2:
        print("  Note: No reports found for MSFT 2023 in this test run. Results may vary.")

    # Test Case 3: Fictional company (should ideally yield no results)
    print("\nTest Case 3: Fictional Company ZYX (FCZ), Year 2023")
    reports3 = agent.get_financial_reports("Fictional Company ZYX", "FCZ", "2023")
    print(f"Found {len(reports3)} reports for fictional company (expected 0).")
    if reports3:
        print("  WARNING: Found reports for a fictional company, this might indicate very broad search results.")

    print("\n--- FinancialReportAgent Test Complete ---")
