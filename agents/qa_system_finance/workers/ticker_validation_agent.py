"""
Ticker Symbol Validation Agent.

This module provides a function to validate if a given stock ticker symbol
is recognized by the yfinance library, typically indicating it's a valid
or at least known symbol.
"""
import yfinance

def validate_ticker(ticker_symbol: str) -> bool:
    """
    Validates if a given ticker symbol is valid using the yfinance library.

    A ticker is considered valid if yfinance can retrieve some basic information
    or historical data for it. This function tries to fetch a minimal piece of
    data ('1d' history) or ticker info.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., "AAPL", "MSFT") to validate.

    Returns:
        True if the ticker symbol appears to be valid (yfinance found data/info),
        False otherwise (e.g., yfinance raised an exception or returned no meaningful data).
    """
    if not ticker_symbol: # Basic check for empty string
        return False

    try:
        # Create a Ticker object for the given symbol
        ticker = yfinance.Ticker(ticker_symbol)

        # Attempt to fetch a small piece of historical data.
        # This is often faster than fetching .info if the ticker is invalid.
        # If history is not empty, the ticker is likely valid.
        if not ticker.history(period="1d").empty:
            return True
        # As a fallback, if history is empty (e.g., for some specific asset types or
        # new listings where '1d' might not yet be available), try checking .info.
        # .info can be slow or unreliable for some invalid/delisted tickers,
        # but it's a more comprehensive check.
        # yfinance often returns an empty dict or raises an error for bad tickers here.
        elif ticker.info and len(ticker.info) > 1: # Check if info is not empty and has more than just symbol
            # len(ticker.info) > 1 is a heuristic: sometimes a valid but obscure ticker might return
            # a dict with just the symbol if no other info is found.
            # A more robust check might be looking for specific keys like 'shortName' or 'longName',
            # but those aren't guaranteed for all asset types.
            return True
        else:
            # If both history is empty and info is minimal/empty, consider it invalid.
            return False

    except Exception as e:
        # If yfinance raises any exception during the process (e.g., for a completely
        # bogus ticker symbol, network issues, etc.), consider it invalid.
        # print(f"Validation error for {ticker_symbol}: {e}") # Optional: log for debugging
        return False

if __name__ == '__main__':
    # Test cases for direct execution and manual verification
    valid_tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "BRK-B"]
    # Invalid tickers - some might be old symbols, some purely fictional
    invalid_tickers = ["INVALIDTICKERXYZ", "NONEXISTENT", "12345", "GOOG.XYZ"]

    print("--- Testing Ticker Validation ---")
    print("\nTesting known valid tickers:")
    for ticker_sym in valid_tickers:
        is_valid = validate_ticker(ticker_sym)
        print(f"Is '{ticker_sym}' valid? {is_valid}")
        if not is_valid:
            print(f"  ERROR: Expected '{ticker_sym}' to be VALID but was reported as INVALID.")

    print("\nTesting known invalid tickers:")
    for ticker_sym in invalid_tickers:
        is_valid = validate_ticker(ticker_sym)
        print(f"Is '{ticker_sym}' valid? {is_valid}")
        if is_valid:
            print(f"  ERROR: Expected '{ticker_sym}' to be INVALID but was reported as VALID.")

    print("\n--- Validation Test Complete ---")
