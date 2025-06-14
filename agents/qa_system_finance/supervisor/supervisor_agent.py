"""
Supervisor Agent for the Financial QA System.

This module defines the SupervisorAgent class, which orchestrates the workflow
of the financial question-answering system. It interacts with the user to get
input (ticker symbol, period), then delegates tasks to various worker agents
(e.g., for stock prices, news, financial reports), and finally consolidates
their findings into a structured JSON output.
"""
import yfinance as yf
from datetime import datetime, timedelta
import json # Imported in main.py for final output, but good to have if used here.

# Import worker agents from the workers package
from agents.qa_system_finance.workers import (
    StockPriceAgent,
    FinancialReportAgent,
    CompanyNewsAgent,
    MarketNewsAgent
)
# Import utility functions
from agents.qa_system_finance.workers.ticker_validation_agent import validate_ticker
from agents.qa_system_finance.utils.date_utils import get_monday_of_week


class SupervisorAgent:
    """
    Orchestrates the financial data gathering and reporting process.

    This agent manages user interaction, calls various specialized worker agents,
    and compiles their results into a comprehensive report.
    """
    def __init__(self):
        """
        Initializes the SupervisorAgent and its worker agents.
        Sets up instances of all required worker agents and initializes
        internal state variables for ticker information and output.
        """
        self.stock_price_agent = StockPriceAgent()
        self.financial_report_agent = FinancialReportAgent()
        self.company_news_agent = CompanyNewsAgent()
        self.market_news_agent = MarketNewsAgent()
        self.ticker_info = None  # To store fetched ticker information (e.g., company name)
        self.last_output = None  # To store the most recent JSON output object

    def get_ticker_input(self) -> str | None:
        """
        Prompts the user for a stock ticker symbol and validates it.

        It continuously asks for input until a valid ticker symbol is provided
        by the user. Upon validation, it attempts to fetch basic company
        information using yfinance.

        Returns:
            The validated ticker symbol as a string (e.g., "AAPL").
            Returns None if critical information cannot be fetched or input fails,
            though current implementation tends to fallback.
        """
        while True:
            ticker_symbol = input("分析対象のティッカーシンボルを入力してください (例: AAPL, MSFT): ").strip().upper()
            if not ticker_symbol:
                print("ティッカーシンボルが入力されていません。再度入力してください。")
                continue

            if validate_ticker(ticker_symbol):
                try:
                    # Fetch ticker object from yfinance
                    ticker_obj = yf.Ticker(ticker_symbol)
                    # Attempt to get company info. This can sometimes be slow or fail.
                    # A quick check like history might be an alternative pre-check.
                    if not ticker_obj.history(period="1d").empty:
                        self.ticker_info = ticker_obj.info
                    else: # If history is empty, .info might also fail or be empty
                        self.ticker_info = {} # Ensure it's a dict to avoid attribute errors

                    # Validate if essential info like 'longName' was fetched.
                    # Provide a fallback if detailed info is missing.
                    if not self.ticker_info or not self.ticker_info.get('longName'):
                        print(f"詳細な企業名を取得できませんでした。ティッカーシンボル '{ticker_symbol}' を企業名として使用します。")
                        self.ticker_info = {'longName': ticker_symbol, 'shortName': ticker_symbol}

                    # If ticker_info ended up empty for some reason
                    if not self.ticker_info:
                         self.ticker_info = {'longName': ticker_symbol, 'shortName': ticker_symbol}

                    print(f"企業名: {self.ticker_info.get('longName', ticker_symbol)}")
                    return ticker_symbol
                except Exception as e:
                    print(f"企業情報の取得中にエラーが発生しました ({ticker_symbol}): {e}")
                    # Fallback: use the ticker symbol itself as the company name
                    self.ticker_info = {'longName': ticker_symbol, 'shortName': ticker_symbol}
                    return ticker_symbol # Allow proceeding with the ticker symbol
            else:
                print("ご指定のティッカーシンボルは見つかりませんでした。再度入力してください。")

    def get_period_input(self) -> tuple[str, int]:
        """
        Prompts the user for the analysis period offset in weeks.

        Calculates the Monday of the target week based on the user-provided offset.
        0 means current week, 1 means last week, and so on.

        Returns:
            A tuple containing:
            - monday_date_str: The date string of the Monday of the target week ("YYYY-MM-DD").
            - week_offset: The original integer offset provided by the user.
        """
        while True:
            try:
                period_offset_str = input("分析対象の期間を週単位で指定してください（例: 「今週」なら0, 「先週」なら1, 「2週間前」なら2): ")
                week_offset = int(period_offset_str)
                if week_offset < 0:
                    print("週のオフセットは0以上の整数で入力してください。")
                    continue

                # Use utility function to get the Monday of the specified week
                monday_date_str = get_monday_of_week(week_offset)
                return monday_date_str, week_offset
            except ValueError:
                print("無効な入力です。整数で週のオフセットを入力してください。")
            except Exception as e:
                # Catch any other unexpected errors during period processing
                print(f"期間の処理中にエラーが発生しました: {e}")
                # Fallback to current week if an error occurs
                # This ensures the application can attempt to proceed
                print("デフォルトで今週の期間を使用します。")
                return get_monday_of_week(0), 0


    def run(self) -> dict | None:
        """
        Runs the main financial analysis workflow.

        This method coordinates the process:
        1. Gets ticker and period input from the user.
        2. Calculates relevant date ranges.
        3. Calls various worker agents to fetch stock data, financial reports, and news.
        4. Compiles all information into a structured dictionary.
        5. Generates a simple overall summary.
        6. Stores and returns the final dictionary.

        Returns:
            A dictionary containing the consolidated financial analysis data,
            or None if the process is aborted early (e.g., ticker input fails critically).
        """
        print("--- Financial Analysis Supervisor ---")

        ticker_symbol = self.get_ticker_input()
        # If ticker input fails in a way that get_ticker_input returns None (currently it doesn't)
        if not ticker_symbol:
            print("ティッカーシンボルが取得できなかったため、処理を終了します。")
            self.last_output = None
            return None

        monday_date_str, week_offset = self.get_period_input()

        try:
            start_date_obj = datetime.strptime(monday_date_str, "%Y-%m-%d")
        except ValueError:
            # This case should ideally be rare if get_monday_of_week is robust
            print(f"内部日付形式エラー: {monday_date_str}。処理を継続できません。")
            self.last_output = {"error": "Internal date format error."}
            return self.last_output

        # Calculate end date for yfinance (Saturday to include Friday's data)
        end_date_for_yfinance_obj = start_date_obj + timedelta(days=5)
        end_date_for_yfinance_str = end_date_for_yfinance_obj.strftime("%Y-%m-%d")

        # Calculate display end date (Friday)
        friday_display_date_obj = start_date_obj + timedelta(days=4)
        friday_display_date_str = friday_display_date_obj.strftime("%Y-%m-%d")

        # Prepare common parameters for worker agents
        company_name = self.ticker_info.get('longName', ticker_symbol) if self.ticker_info else ticker_symbol
        year = str(start_date_obj.year)
        month_name = start_date_obj.strftime("%B") # Full month name, e.g., "July"
        period_description_week = f"the week of {monday_date_str} to {friday_display_date_str}"

        print(f"\n分析を開始します: {company_name} ({ticker_symbol})")
        print(f"分析期間: {monday_date_str} から {friday_display_date_str}\n")

        # --- Call Worker Agents ---
        stock_data = {"data": [], "summary": "Stock data retrieval was not attempted or failed."}
        try:
            print("株価情報を取得中...")
            stock_data = self.stock_price_agent.get_stock_prices(ticker_symbol, monday_date_str, end_date_for_yfinance_str)
        except Exception as e:
            print(f"株価情報の取得中に予期せぬエラー: {e}")
            stock_data = {"data": [], "summary": f"Failed to retrieve stock price data due to an unexpected error: {e}"}

        financial_reports = []
        try:
            print("財務レポートを検索中...")
            financial_reports = self.financial_report_agent.get_financial_reports(company_name, ticker_symbol, year)
        except Exception as e:
            print(f"財務レポートの検索中に予期せぬエラー: {e}")
            # Ensure it's a list of dicts as expected by output structure for error cases
            financial_reports = [{"title": f"Failed to retrieve financial reports due to an unexpected error: {e}", "url": "", "summary": ""}]


        company_news = []
        try:
            print("企業ニュースを検索中...")
            company_news = self.company_news_agent.get_company_news(company_name, ticker_symbol, period_description_week)
        except Exception as e:
            print(f"企業ニュースの検索中に予期せぬエラー: {e}")
            company_news = [{"title": f"Failed to retrieve company news due to an unexpected error: {e}", "url": "", "summary": ""}]

        market_news = []
        try:
            print("市場ニュースを検索中...")
            market_period_description = f"{month_name} {year}" # General market news for the month
            market_news = self.market_news_agent.get_market_news(year, month_name, market_period_description)
        except Exception as e:
            print(f"市場ニュースの検索中に予期せぬエラー: {e}")
            market_news = [{"title": f"Failed to retrieve market news due to an unexpected error: {e}", "url": "", "summary": ""}]

        # --- Construct Overall Summary ---
        summary_parts = []
        summary_parts.append(f"{company_name} ({ticker_symbol}) の {monday_date_str} 開始週の分析結果。")

        # Stock data summary
        if stock_data and stock_data.get('data'):
            summary_parts.append(stock_data.get('summary', "株価データを取得しました。"))
        elif stock_data and "error" in stock_data.get('summary', "").lower():
            summary_parts.append(f"株価データの取得に失敗しました: {stock_data.get('summary')}")
        elif stock_data and "No stock price data found" in stock_data.get('summary', ""):
             summary_parts.append("指定された期間の株価データは見つかりませんでした。")
        else:
            summary_parts.append("株価データの取得に失敗しました。")


        # Financial reports summary
        if financial_reports and not (len(financial_reports) == 1 and "Failed to retrieve" in financial_reports[0].get("title", "")):
            summary_parts.append(f"{len(financial_reports)}件の財務レポート関連情報が見つかりました。")
        else:
            summary_parts.append("財務レポートの検索で問題が発生したか、関連情報が見つかりませんでした。")
            if financial_reports and financial_reports[0].get("title"):
                 summary_parts.append(f"詳細: {financial_reports[0]['title']}")


        # Company news summary
        if company_news and not (len(company_news) == 1 and "Failed to retrieve" in company_news[0].get("title", "")):
            summary_parts.append(f"{len(company_news)}件の企業ニュース記事が見つかりました。")
        else:
            summary_parts.append("企業ニュースの検索で問題が発生したか、記事が見つかりませんでした。")
            if company_news and company_news[0].get("title"):
                 summary_parts.append(f"詳細: {company_news[0]['title']}")

        # Market news summary
        if market_news and not (len(market_news) == 1 and "Failed to retrieve" in market_news[0].get("title", "")):
            summary_parts.append(f"{len(market_news)}件の市場ニュース記事が見つかりました。")
        else:
            summary_parts.append("市場ニュースの検索で問題が発生したか、記事が見つかりませんでした。")
            if market_news and market_news[0].get("title"):
                 summary_parts.append(f"詳細: {market_news[0]['title']}")

        overall_summary_str = " ".join(summary_parts)

        # --- Compile Final Output ---
        output = {
            "ticker": ticker_symbol,
            "companyName": company_name,
            "analysisPeriod": {
                "start": monday_date_str,
                "end": friday_display_date_str
            },
            "stockPrice": stock_data if stock_data else {"data": [], "summary": "株価データの取得に失敗しました。"},
            "financialReports": financial_reports if financial_reports is not None else [{"title": "財務レポートの取得に失敗しました。", "url": "", "summary": ""}],
            "companyNews": company_news if company_news is not None else [{"title": "企業ニュースの取得に失敗しました。", "url": "", "summary": ""}],
            "marketNews": market_news if market_news is not None else [{"title": "市場ニュースの取得に失敗しました。", "url": "", "summary": ""}],
            "overallSummary": overall_summary_str
        }

        print("\n--- 分析結果 ---")
        self.last_output = output
        print("分析が完了しました。結果は self.last_output に保存されています。")
        print("-------------------")
        return self.last_output

if __name__ == '__main__':
    # This section allows direct execution of the supervisor agent for testing.
    # User will be prompted for inputs in the console.
    print("--- Supervisor Agent Direct Execution Mode ---")
    agent = SupervisorAgent()
    final_data = agent.run()
    if final_data:
        print("\n=== Direct Execution Output (JSON) ===")
        # Pretty print the JSON output
        print(json.dumps(final_data, indent=2, ensure_ascii=False))
        print("======================================")
