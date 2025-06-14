from adk.agent import LlmAgent
from adk.config import CommonAgentConfig
from agents.qa_system_finance.tools.yahoo_finance_tools import get_financial_summary

class FinancialSummaryAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            config=CommonAgentConfig(
                llm_config_template_path=None # Using default Gemini Pro
            ),
            default_tools=[get_financial_summary]
        )

    def get_summary(self, ticker: str) -> dict:
        """
        Retrieves financial summary for the given ticker.
        """
        prompt = f"Please fetch the financial summary for ticker '{ticker}'. Use the get_financial_summary tool and return its exact output."

        response = self.chat(prompt) # Assuming sync chat; use await self.chat(prompt) if in async context

        if response.tool_calls and response.tool_calls[0].name == "get_financial_summary":
            return response.tool_calls[0].output

        return {"error": "LLM did not return tool output as expected or failed to use the tool."}

if __name__ == '__main__':
    # Example Usage (requires Google API key for LLM & yfinance to fetch data)
    try:
        agent = FinancialSummaryAgent()

        ticker_to_test = "AAPL" # Apple Inc.
        print(f"Retrieving financial summary for ticker: {ticker_to_test}")
        summary_result = agent.get_summary(ticker_to_test)

        if "summary" in summary_result:
            print(f"Financial Summary for {summary_result['summary'].get('shortName', ticker_to_test)}:")
            for key, value in summary_result['summary'].items():
                print(f"  {key}: {value}")
        elif "warning" in summary_result:
            print(f"Warning: {summary_result['warning']}")
        elif "error" in summary_result:
            print(f"Error retrieving summary: {summary_result['error']}")
        else:
            print(f"Unexpected result: {summary_result}")

        print("\n--- Test with a non-stock ticker (e.g., an ETF like 'SPY') ---")
        etf_ticker = "SPY"
        print(f"Retrieving financial summary for ticker: {etf_ticker}")
        summary_etf = agent.get_summary(etf_ticker)
        if "summary" in summary_etf:
            print(f"Financial Summary for {summary_etf['summary'].get('shortName', etf_ticker)}:")
            for key, value in summary_etf['summary'].items():
                print(f"  {key}: {value}")
        elif "warning" in summary_etf: # ETFs might have less data, yfinance often returns some info though
            print(f"Warning for {etf_ticker}: {summary_etf['warning']}")
            print(f"Data: {summary_etf.get('summary', {})}")
        elif "error" in summary_etf:
            print(f"Error for {etf_ticker}: {summary_etf['error']}")
        else:
            print(f"Unexpected result for {etf_ticker}: {summary_etf}")


    except Exception as e:
        print(f"An error occurred during example usage: {e}")
        print("Please ensure your Google API key is set up and yfinance can access data.")
