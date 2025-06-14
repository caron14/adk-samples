import yfinance as yf
from adk.tools import tool

@tool
def is_ticker_valid(ticker_symbol: str) -> dict:
    """
    Validates a stock ticker symbol using Yahoo Finance.
    Returns a dictionary with 'valid': True and 'info': data if valid,
    or 'valid': False and 'error': message if invalid or an error occurs.
    """
    try:
        ticker_obj = yf.Ticker(ticker_symbol)
        # Attempt to fetch info. If the ticker is invalid, this often returns an empty dict
        # or specific error structure, depending on yfinance version.
        # A more robust check is to see if history is available for a short period.
        hist = ticker_obj.history(period="1d")
        if hist.empty:
            # Some invalid tickers might still not raise an exception but return empty history.
            # Or check if info dictionary has minimal expected data.
            if not ticker_obj.info or 'symbol' not in ticker_obj.info:
                 return {"valid": False, "error": f"Ticker {ticker_symbol} seems invalid or no data available."}
            # If info has symbol, treat as valid but potentially delisted or very new.
            # For this agent, we'll consider it valid if yf.Ticker doesn't error out severely
            # and can at least provide a symbol in its info.
        return {"valid": True, "info": ticker_obj.info.get('shortName', ticker_symbol)}
    except Exception as e:
        # Catching generic exceptions from yfinance, which can vary.
        return {"valid": False, "error": f"Error validating ticker {ticker_symbol}: {str(e)}"}

@tool
def get_financial_summary(ticker_symbol: str) -> dict:
    """
    Retrieves a financial summary for a given stock ticker using Yahoo Finance.
    Returns a dictionary with key financial data or an error message.
    """
    try:
        ticker_obj = yf.Ticker(ticker_symbol)
        info = ticker_obj.info

        if not info or 'symbol' not in info: # Basic check if info was retrieved
            return {"error": f"Could not retrieve financial info for {ticker_symbol}. It might be an invalid ticker."}

        # Extract relevant financial data. Availability can vary.
        summary = {
            "symbol": info.get("symbol"),
            "shortName": info.get("shortName"),
            "longName": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "marketCap": info.get("marketCap"),
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "pegRatio": info.get("pegRatio"),
            "priceToBook": info.get("priceToBook"),
            "enterpriseValue": info.get("enterpriseValue"),
            "revenueGrowth": info.get("revenueGrowth"), # Quarterly
            "earningsGrowth": info.get("earningsGrowth"), # Quarterly
            "returnOnEquity": info.get("returnOnEquity"),
            "debtToEquity": info.get("debtToEquity"),
            "dividendYield": info.get("dividendYield"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            "averageVolume": info.get("averageVolume"),
            "currentPrice": info.get("currentPrice", info.get("regularMarketPrice")),
            "recommendationKey": info.get("recommendationKey"),
            "financialCurrency": info.get("financialCurrency")
        }

        # Filter out None values for a cleaner summary
        summary_filtered = {k: v for k, v in summary.items() if v is not None}

        if not summary_filtered or len(summary_filtered) <= 3 : # If only symbol/name/currency came back
             return {"warning": f"Limited financial data found for {ticker_symbol}. It may be a non-stock entity or data is sparse."}

        return {"summary": summary_filtered}

    except Exception as e:
        return {"error": f"Error retrieving financial summary for {ticker_symbol}: {str(e)}"}
