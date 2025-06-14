import unittest
from unittest.mock import patch, MagicMock, call
import json
from agents.qa_system_finance.supervisor.supervisor_agent import SupervisorAgent
# Assuming other necessary imports from supervisor_agent or its dependencies are handled by mocks

class TestSupervisorAgent(unittest.TestCase):

    def setUp(self):
        # It's good practice to mock dependencies of the class being tested if they make external calls
        # For SupervisorAgent, this includes yf.Ticker, validate_ticker, get_monday_of_week, and all worker agents

        # Patch worker agents (they are instantiated in SupervisorAgent's __init__)
        patcher_stock = patch('agents.qa_system_finance.supervisor.supervisor_agent.StockPriceAgent', MagicMock())
        patcher_fin_report = patch('agents.qa_system_finance.supervisor.supervisor_agent.FinancialReportAgent', MagicMock())
        patcher_comp_news = patch('agents.qa_system_finance.supervisor.supervisor_agent.CompanyNewsAgent', MagicMock())
        patcher_market_news = patch('agents.qa_system_finance.supervisor.supervisor_agent.MarketNewsAgent', MagicMock())

        self.mock_stock_agent_class = patcher_stock.start()
        self.mock_fin_report_agent_class = patcher_fin_report.start()
        self.mock_comp_news_agent_class = patcher_comp_news.start()
        self.mock_market_news_agent_class = patcher_market_news.start()

        # Instantiate the actual agent instances that will be used by Supervisor
        self.mock_stock_agent_instance = self.mock_stock_agent_class.return_value
        self.mock_fin_report_agent_instance = self.mock_fin_report_agent_class.return_value
        self.mock_comp_news_agent_instance = self.mock_comp_news_agent_class.return_value
        self.mock_market_news_agent_instance = self.mock_market_news_agent_class.return_value

        self.addCleanup(patcher_stock.stop)
        self.addCleanup(patcher_fin_report.stop)
        self.addCleanup(patcher_comp_news.stop)
        self.addCleanup(patcher_market_news.stop)

        self.supervisor = SupervisorAgent()
        # The __init__ of SupervisorAgent has now run, and self.supervisor has mocked agent instances

    @patch('agents.qa_system_finance.supervisor.supervisor_agent.validate_ticker')
    @patch('agents.qa_system_finance.supervisor.supervisor_agent.get_monday_of_week')
    @patch('builtins.input')
    @patch('yfinance.Ticker') # Mock yf.Ticker called in get_ticker_input
    @patch('builtins.print') # To capture print output from supervisor's own print statements
    def test_run_workflow_success(self, mock_print, mock_yf_ticker, mock_input, mock_get_monday, mock_validate_ticker):
        # --- Setup Mocks ---
        # 1. User Inputs
        mock_input.side_effect = ["AAPL", "1"] # Ticker, then period offset

        # 2. Ticker Validation and Info
        mock_validate_ticker.return_value = True
        mock_ticker_info = {'longName': 'Apple Inc.', 'shortName': 'Apple'}
        mock_yf_ticker_instance = MagicMock()
        mock_yf_ticker_instance.info = mock_ticker_info
        mock_yf_ticker_instance.history.return_value = MagicMock(empty=False) # Simulate non-empty history
        mock_yf_ticker.return_value = mock_yf_ticker_instance

        # 3. Date Utils
        mock_get_monday.return_value = "2023-07-17" # Monday for week_offset=1 (example)

        # 4. Worker Agent Responses
        self.mock_stock_agent_instance.get_stock_prices.return_value = {"data": [{"date": "2023-07-17", "close": 150}], "summary": "Stock data ok"}
        self.mock_fin_report_agent_instance.get_financial_reports.return_value = [{"title": "Q2 Report", "url": "url1", "summary": "Good results"}]
        self.mock_comp_news_agent_instance.get_company_news.return_value = [{"title": "New iPhone", "url": "url2", "summary": "Launch soon"}]
        self.mock_market_news_agent_instance.get_market_news.return_value = [{"title": "Market Rally", "url": "url3", "summary": "Stocks up"}]

        # --- Execute ---
        # Modify run to return the dictionary instead of printing for easier testing,
        # or capture print output. For now, we'll capture json.dumps.
        # If supervisor.run() is modified to store output in self.last_output as suggested:
        # self.supervisor.run()
        # final_output = self.supervisor.last_output
        # For now, assuming it still prints, json.dumps will be called

        # self.supervisor.run() # This will call json.dumps internally if not changed
        # The run method now returns the output and stores it in self.last_output
        final_output_dict = self.supervisor.run()


        # --- Assertions ---
        # 1. Inputs and Date Utils Called
        mock_input.assert_any_call("分析対象のティッカーシンボルを入力してください (例: AAPL, MSFT): ")
        mock_input.assert_any_call("分析対象の期間を週単位で指定してください（例: 「今週」なら0, 「先週」なら1, 「2週間前」なら2): ")
        mock_validate_ticker.assert_called_once_with("AAPL")
        mock_yf_ticker.assert_called_once_with("AAPL")
        mock_get_monday.assert_called_once_with(1) # week_offset = 1

        # 2. Worker Agents Called with Correct Parameters
        # Expected dates: start=2023-07-17 (Monday), yf_end=2023-07-22 (Saturday)
        # company_name = 'Apple Inc.', year = '2023', month_name = 'July'
        # period_description_week = "the week of 2023-07-17 to 2023-07-21"

        self.mock_stock_agent_instance.get_stock_prices.assert_called_once_with("AAPL", "2023-07-17", "2023-07-22")
        self.mock_fin_report_agent_instance.get_financial_reports.assert_called_once_with("Apple Inc.", "AAPL", "2023")
        self.mock_comp_news_agent_instance.get_company_news.assert_called_once_with("Apple Inc.", "AAPL", "the week of 2023-07-17 to 2023-07-21")
        self.mock_market_news_agent_instance.get_market_news.assert_called_once_with("2023", "July", "July 2023")

        # 3. Output Structure (checking the dictionary returned by run())
        self.assertIsNotNone(final_output_dict) # Ensure something was returned
        self.assertEqual(final_output_dict["ticker"], "AAPL")
        self.assertEqual(final_output_dict["companyName"], "Apple Inc.")
        self.assertEqual(final_output_dict["analysisPeriod"]["start"], "2023-07-17")
        self.assertEqual(final_output_dict["analysisPeriod"]["end"], "2023-07-21") # Friday
        self.assertEqual(final_output_dict["stockPrice"]["summary"], "Stock data ok")
        self.assertEqual(final_output_dict["financialReports"][0]["title"], "Q2 Report")
        self.assertEqual(final_output_dict["companyNews"][0]["title"], "New iPhone")
        self.assertEqual(final_output_dict["marketNews"][0]["title"], "Market Rally")
        self.assertEqual(final_output_dict["overallSummary"], "総合的な要約は後ほど実装されます。")

    # Add more tests for failure cases, invalid inputs, etc.
    # For example, test what happens if validate_ticker returns False repeatedly (if not an infinite loop)
    # Test what happens if yf.Ticker().info is empty or lacks 'longName'

if __name__ == '__main__':
    unittest.main()
