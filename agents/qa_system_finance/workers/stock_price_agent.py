"""
Stock Price Agent.

This module defines the StockPriceAgent class, responsible for fetching historical
stock price data for a given ticker symbol over a specified period using the
yfinance library.
"""
import yfinance
import pandas as pd
import datetime # Used in yfinance, but not directly in this agent's current code.

class StockPriceAgent:
    """
    Agent responsible for fetching historical stock price data.

    Uses the yfinance library to retrieve daily open, close, high, low, and volume
    for a specified ticker symbol and date range.
    """

    def get_stock_prices(self, ticker_symbol: str, start_date: str, end_date: str) -> dict:
        """
        Fetches historical stock prices for a given ticker symbol and date range.

        The end_date for yfinance's history method is typically exclusive for daily data.
        The supervisor is expected to pass an adjusted end_date (e.g., Saturday if
        the desired period is Monday-Friday) to ensure all requested days are included.

        Args:
            ticker_symbol: The stock ticker symbol (e.g., "AAPL").
            start_date: The start date for fetching data (YYYY-MM-DD format).
            end_date: The end date for fetching data (YYYY-MM-DD format).
                      This should be the day *after* the last desired data point
                      if fetching daily data, due to yfinance's exclusivity.

        Returns:
            A dictionary containing:
            - "data": A list of dictionaries, where each inner dictionary represents
                      a day's stock data (date, open, close, high, low, volume).
                      Empty if no data is found or an error occurs.
            - "summary": A string summarizing the outcome of the operation (e.g.,
                         number of data points fetched, or an error message).
        """
        formatted_data_list = []
        try:
            # Input validation (basic)
            if not ticker_symbol or not start_date or not end_date:
                return {"data": [], "summary": "Ticker symbol, start date, or end date missing."}

            ticker = yfinance.Ticker(ticker_symbol)

            # Fetch historical data. The supervisor adjusts end_date to be exclusive.
            # For example, for Mon-Fri data, end_date might be Saturday.
            hist_data = ticker.history(start=start_date, end=end_date)

            if hist_data.empty:
                return {"data": [], "summary": "No stock price data found for the period."}

            # Iterate through the DataFrame rows (each row is a trading day)
            for index_date, row in hist_data.iterrows():
                # The index (index_date) is usually a pandas Timestamp object.
                # Convert it to "YYYY-MM-DD" string format.
                if isinstance(index_date, pd.Timestamp):
                    date_str = index_date.strftime('%Y-%m-%d')
                else:
                    # Should not typically happen with yfinance history index
                    date_str = str(index_date)

                formatted_data_list.append({
                    "date": date_str,
                    "open": row.get('Open'), # Using .get() for safety, though keys should exist
                    "close": row.get('Close'),
                    "high": row.get('High'),
                    "low": row.get('Low'),
                    "volume": row.get('Volume')
                })

            summary_msg = (f"Successfully fetched {len(formatted_data_list)} days of stock price data "
                           f"for {ticker_symbol} from {start_date} up to (but not including) {end_date}.")
            return {"data": formatted_data_list, "summary": summary_msg}

        except Exception as e:
            # Log the exception or handle it more gracefully in a real app
            error_summary = f"An error occurred while fetching stock price data for {ticker_symbol}: {str(e)}"
            print(error_summary) # Print error for visibility during execution
            return {"data": [], "summary": error_summary}

if __name__ == '__main__':
    # Example usage for testing the agent directly
    agent = StockPriceAgent()

    print("--- Testing StockPriceAgent ---")

    # Test case 1: Valid ticker and date range (e.g., Apple for a week in 2023)
    # Supervisor would calculate end_date as '2023-07-08' (Saturday) to get data up to Friday '2023-07-07'.
    print("\nTest Case 1: AAPL, from 2023-07-03 to 2023-07-08 (expects data for Mon-Fri)")
    prices1 = agent.get_stock_prices("AAPL", "2023-07-03", "2023-07-08") # Mon to Sat (exclusive)
    print(f"Data points found: {len(prices1['data'])}")
    # print(f"Data: {prices1['data']}") # Can be verbose
    print(f"Summary: {prices1['summary']}")
    if not prices1['data']:
        print("  WARNING: Test Case 1 returned no data. Check yfinance or dates if this is unexpected.")
    for item in prices1.get('data', []):
        if not all(k in item and item[k] is not None for k in ["date", "open", "close", "high", "low", "volume"]):
            print(f"  ERROR: Test Case 1 data item missing or has None keys: {item}")
            break

    # Test case 2: Period with no trading (e.g., New Year's Day if it's the entire range)
    print("\nTest Case 2: GOOG, from 2024-01-01 to 2024-01-02 (New Year's Day, next day)")
    prices2 = agent.get_stock_prices("GOOG", "2024-01-01", "2024-01-02")
    print(f"Data points found: {len(prices2['data'])}")
    print(f"Summary: {prices2['summary']}")
    if prices2['data'] and "No stock price data found" not in prices2['summary']:
        print("  ERROR: Test Case 2 expected no data or 'No data' summary.")

    # Test case 3: Invalid ticker
    print("\nTest Case 3: INVALIDTICKERXYZ, from 2023-01-01 to 2023-01-05")
    prices3 = agent.get_stock_prices("INVALIDTICKERXYZ", "2023-01-01", "2023-01-05")
    print(f"Data points found: {len(prices3['data'])}")
    print(f"Summary: {prices3['summary']}")
    if prices3['data']:
        print("  ERROR: Test Case 3 returned data for an invalid ticker.")
    if not ("No stock price data found" in prices3['summary'] or "error occurred" in prices3['summary']):
         print(f"  WARNING: Test Case 3 summary might be unexpected for invalid ticker: {prices3['summary']}")

    print("\n--- StockPriceAgent Test Complete ---")
