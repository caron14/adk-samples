import unittest
from unittest.mock import MagicMock, patch

# Import agent classes
from agents.qa_system_finance.workers.financial_report_agent import FinancialReportAgent
from agents.qa_system_finance.workers.company_news_agent import CompanyNewsAgent
from agents.qa_system_finance.workers.market_news_agent import MarketNewsAgent

class TestFinancialReportAgent(unittest.TestCase):

    def setUp(self):
        self.agent = FinancialReportAgent()

    @patch('agents.qa_system_finance.workers.financial_report_agent.DDGS')
    def test_get_financial_reports_success(self, mock_ddgs_class):
        mock_ddgs_instance = MagicMock()
        mock_search_results = [
            {'title': 'Report 1', 'href': 'http://example.com/report1', 'body': 'Summary 1'},
            {'title': 'Report 2', 'href': 'http://example.com/report2', 'body': 'Summary 2'}
        ]
        mock_ddgs_instance.text.return_value = mock_search_results
        mock_ddgs_class.return_value = mock_ddgs_instance

        result = self.agent.get_financial_reports("Apple Inc.", "AAPL", "2022")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Report 1')
        self.assertEqual(result[0]['url'], 'http://example.com/report1')
        self.assertEqual(result[0]['summary'], 'Summary 1')
        mock_ddgs_instance.text.assert_called_once()

    @patch('agents.qa_system_finance.workers.financial_report_agent.DDGS')
    def test_get_financial_reports_no_results(self, mock_ddgs_class):
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = []
        mock_ddgs_class.return_value = mock_ddgs_instance

        result = self.agent.get_financial_reports("NonExistent Inc.", "NEXI", "2023")

        self.assertEqual(len(result), 0)
        mock_ddgs_instance.text.assert_called_once()

    @patch('agents.qa_system_finance.workers.financial_report_agent.DDGS')
    def test_get_financial_reports_api_error(self, mock_ddgs_class):
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.side_effect = Exception("DDGS API Error")
        mock_ddgs_class.return_value = mock_ddgs_instance

        result = self.agent.get_financial_reports("Error Corp", "ERR", "2023")
        self.assertEqual(len(result), 0)

class TestCompanyNewsAgent(unittest.TestCase):

    def setUp(self):
        self.agent = CompanyNewsAgent()

    @patch('agents.qa_system_finance.workers.company_news_agent.DDGS')
    def test_get_company_news_success(self, mock_ddgs_class):
        mock_ddgs_instance = MagicMock()
        mock_search_results = [
            {'title': 'News A', 'href': 'http://example.com/newsA', 'body': 'Body A'},
        ]
        mock_ddgs_instance.text.return_value = mock_search_results
        mock_ddgs_class.return_value = mock_ddgs_instance

        result = self.agent.get_company_news("Tesla", "TSLA", "past week")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'News A')
        mock_ddgs_instance.text.assert_called_once()

    @patch('agents.qa_system_finance.workers.company_news_agent.DDGS')
    def test_get_company_news_no_results(self, mock_ddgs_class):
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = []
        mock_ddgs_class.return_value = mock_ddgs_instance

        result = self.agent.get_company_news("Quiet Inc.", "QINC", "yesterday")
        self.assertEqual(len(result), 0)

class TestMarketNewsAgent(unittest.TestCase):

    def setUp(self):
        self.agent = MarketNewsAgent()

    @patch('agents.qa_system_finance.workers.market_news_agent.DDGS')
    def test_get_market_news_success(self, mock_ddgs_class):
        mock_ddgs_instance = MagicMock()
        mock_search_results = [
            {'title': 'Market Update', 'href': 'http://example.com/market_update', 'body': 'Market is up.'},
            {'title': 'Economic Outlook', 'href': 'http://example.com/econ_outlook', 'body': 'Outlook is stable.'}
        ]
        mock_ddgs_instance.text.return_value = mock_search_results
        mock_ddgs_class.return_value = mock_ddgs_instance

        result = self.agent.get_market_news("2023", "July", "July 2023")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['summary'], 'Market is up.')
        mock_ddgs_instance.text.assert_called_once()

    @patch('agents.qa_system_finance.workers.market_news_agent.DDGS')
    def test_get_market_news_no_results(self, mock_ddgs_class):
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = []
        mock_ddgs_class.return_value = mock_ddgs_instance

        result = self.agent.get_market_news("1900", "Jan", "January 1900")
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()
