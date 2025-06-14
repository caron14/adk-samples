# This file makes the 'workers' directory a Python package.
# It can also be used to conveniently import worker classes.

from .stock_price_agent import StockPriceAgent
from .financial_report_agent import FinancialReportAgent
from .company_news_agent import CompanyNewsAgent
from .market_news_agent import MarketNewsAgent
from .ticker_validation_agent import validate_ticker # It's a function, but might be useful here too

__all__ = [
    "StockPriceAgent",
    "FinancialReportAgent",
    "CompanyNewsAgent",
    "MarketNewsAgent",
    "validate_ticker" # Exporting the function if it's commonly used with other workers
]

# Test imports (optional, for development convenience)
if __name__ == '__main__':
    print("Testing worker imports...")
    try:
        spa = StockPriceAgent()
        fra = FinancialReportAgent()
        cna = CompanyNewsAgent()
        mna = MarketNewsAgent()
        print("Successfully instantiated all agents.")

        # Example: Call validate_ticker (though it needs a ticker symbol)
        # print(f"validate_ticker function is available: {callable(validate_ticker)}")
        is_aapl_valid = validate_ticker("AAPL") # Requires yfinance, network
        print(f"Is AAPL valid (requires network)? {is_aapl_valid}")

    except ImportError as e:
        print(f"Error importing or instantiating workers: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during test: {e}")
    print("Worker import test complete.")
