from adk.agent import LlmAgent
from adk.config import CommonAgentConfig
from agents.qa_system_finance.tools.duckduckgo_tools import search_news_for_week

class NewsRetrievalAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            config=CommonAgentConfig(
                llm_config_template_path=None # Using default Gemini Pro
            ),
            default_tools=[search_news_for_week]
        )

    def get_news(self, ticker: str, week_monday: str) -> dict:
        """
        Retrieves news for the given ticker and week_monday string (YYYY-MM-DD).
        """
        prompt = f"Please find news for ticker '{ticker}' for the week starting on Monday '{week_monday}'. Use the search_news_for_week tool and return its exact output."

        response = self.chat(prompt)

        if response.tool_calls and response.tool_calls[0].name == "search_news_for_week":
            return response.tool_calls[0].output

        return {"error": "LLM did not return tool output as expected or failed to use the tool."}

if __name__ == '__main__':
    # Example Usage (requires Google API key for LLM)
    try:
        agent = NewsRetrievalAgent()

        # Test with a ticker and a specific Monday date
        ticker_to_test = "MSFT"
        # week_monday_to_test = "2023-10-02" # Example: First week of Oct 2023
        # Let's use a more recent week for potentially more relevant news
        from datetime import datetime, timedelta
        today = datetime.now()
        last_monday = today - timedelta(days=today.weekday() + 7) # Monday of the previous week
        week_monday_to_test = last_monday.strftime("%Y-%m-%d")

        print(f"Retrieving news for ticker: {ticker_to_test}, week of: {week_monday_to_test}")
        news_result = agent.get_news(ticker_to_test, week_monday_to_test)

        if "news_items" in news_result:
            print(f"Found {len(news_result['news_items'])} news items:")
            for item in news_result["news_items"][:3]: # Print first 3
                print(f"  Title: {item['title']}")
                print(f"  Date: {item.get('date', 'N/A')}")
                print(f"  Snippet: {item['body']}")
                print(f"  URL: {item['url']}")
                print("-" * 20)
        elif "error" in news_result:
            print(f"Error retrieving news: {news_result['error']}")
        else:
            print(f"No news found or unexpected result: {news_result}")

    except Exception as e:
        print(f"An error occurred during example usage: {e}")
        print("Please ensure your Google API key is set up if you're running this example.")
