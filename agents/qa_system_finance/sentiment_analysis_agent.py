from adk.agent import LlmAgent
from adk.config import CommonAgentConfig
from agents.qa_system_finance.tools.sentiment_tools import analyze_sentiment

class SentimentAnalysisAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            config=CommonAgentConfig(
                llm_config_template_path=None # Using default Gemini Pro
            ),
            default_tools=[analyze_sentiment]
        )

    def get_sentiment(self, text_content: str) -> dict:
        """
        Analyzes sentiment for the given text content.
        """
        if not text_content:
            return {"error": "Cannot analyze sentiment of empty text."}

        prompt = f"Please analyze the sentiment of the following text: '{text_content}'. Use the analyze_sentiment tool and return its exact output."

        response = self.chat(prompt) # Use await self.chat(prompt) if in async context

        if response.tool_calls and response.tool_calls[0].name == "analyze_sentiment":
            return response.tool_calls[0].output

        return {"error": "LLM did not return tool output as expected or failed to use the tool for sentiment analysis."}

if __name__ == '__main__':
    # Example Usage (requires Google API key for LLM & NLTK VADER lexicon)
    try:
        agent = SentimentAnalysisAgent()

        sample_texts = [
            "Stock prices surged today on positive earnings reports!",
            "The company announced unexpected losses, causing shares to plummet.",
            "Market analysts remain neutral on the stock's future performance.",
            "This is a great product, I love it.",
            "This is a terrible situation, very bad news."
        ]

        for text in sample_texts:
            print(f"Analyzing sentiment for: \"{text}\"")
            sentiment_result = agent.get_sentiment(text)

            if "compound" in sentiment_result: # VADER returns neg, neu, pos, compound
                print(f"  Sentiment: {sentiment_result}")
                compound = sentiment_result['compound']
                if compound >= 0.05:
                    print("  Overall: Positive")
                elif compound <= -0.05:
                    print("  Overall: Negative")
                else:
                    print("  Overall: Neutral")
            elif "error" in sentiment_result:
                print(f"  Error: {sentiment_result['error']}")
            else:
                print(f"  Unexpected result: {sentiment_result}")
            print("-" * 20)

    except Exception as e:
        print(f"An error occurred during example usage: {e}")
        print("Please ensure your Google API key is set up and NLTK VADER lexicon is available.")
