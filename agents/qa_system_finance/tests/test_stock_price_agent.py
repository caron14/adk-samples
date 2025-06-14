import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from agents.qa_system_finance.workers.stock_price_agent import StockPriceAgent

class TestStockPriceAgent(unittest.TestCase):

    def setUp(self):
        self.agent = StockPriceAgent()

    @patch('yfinance.Ticker')
    def test_get_stock_prices_success(self, mock_yf_ticker):
        # Prepare mock data
        mock_data = {
            'Open': [150.0, 151.0],
            'Close': [150.5, 151.5],
            'High': [151.0, 152.0],
            'Low': [149.5, 150.5],
            'Volume': [1000000, 1200000]
        }
        mock_dates = [pd.Timestamp('2023-01-02'), pd.Timestamp('2023-01-03')]
        mock_df = pd.DataFrame(mock_data, index=pd.Index(mock_dates, name="Date"))

        # Configure the mock
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_df
        mock_yf_ticker.return_value = mock_ticker_instance

        # Call the method
        result = self.agent.get_stock_prices("AAPL", "2023-01-02", "2023-01-04") # End date is exclusive in yf

        # Assertions
        self.assertIn("data", result)
        self.assertIn("summary", result)
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["date"], "2023-01-02")
        self.assertEqual(result["data"][0]["open"], 150.0)
        self.assertIn("Successfully fetched 2 days of stock price data", result["summary"])

        mock_yf_ticker.assert_called_once_with("AAPL")
        mock_ticker_instance.history.assert_called_once_with(start="2023-01-02", end="2023-01-04")


    @patch('yfinance.Ticker')
    def test_get_stock_prices_no_data(self, mock_yf_ticker):
        # Configure mock to return empty DataFrame
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = pd.DataFrame() # Empty
        mock_yf_ticker.return_value = mock_ticker_instance

        result = self.agent.get_stock_prices("AAPL", "2023-01-01", "2023-01-02")

        self.assertEqual(result["data"], [])
        self.assertEqual(result["summary"], "No stock price data found for the period.")

    @patch('yfinance.Ticker')
    def test_get_stock_prices_api_error(self, mock_yf_ticker):
        # Configure mock to raise an exception
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.side_effect = Exception("API connection failed")
        mock_yf_ticker.return_value = mock_ticker_instance

        result = self.agent.get_stock_prices("MSFT", "2023-01-01", "2023-01-02")

        self.assertEqual(result["data"], [])
        self.assertTrue("An error occurred while fetching stock price data: API connection failed" in result["summary"])

if __name__ == '__main__':
    unittest.main()
