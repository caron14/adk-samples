from adk.agent import LlmAgent
from adk.config import CommonAgentConfig
from agents.qa_system_finance.tools.yahoo_finance_tools import is_ticker_valid

class TickerValidationAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            config=CommonAgentConfig(
                llm_config_template_path=None # Using default Gemini Pro
            ),
            default_tools=[is_ticker_valid]
        )

    def validate_ticker(self, ticker: str) -> dict:
        """
        Validates the ticker using the is_ticker_valid tool.
        """
        # The prompt can be simple as the tool is quite specific
        prompt = f"Please validate the ticker symbol: {ticker}. Only use the is_ticker_valid tool."

        # For a direct tool call without much LLM reasoning,
        # you might also consider invoking the tool directly if ADK allows easy access,
        # or ensuring the prompt strongly guides the LLM to use the tool and return its output.
        # For now, we assume the LLM will correctly use the tool based on the prompt and tool availability.

        # Let's try to make the LLM's job easier by being more direct.
        # This assumes the LLM can understand to call the tool and return its structured output.
        # A more robust way would be to have the LLM just confirm the intent and then the application code calls the tool.
        # However, for an agent, the LLM is expected to use the tool.

        # Simplified prompt focusing on tool use:
        prompt_for_tool_use = f"Use the is_ticker_valid tool for the ticker '{ticker}' and return its exact output."

        response = self.chat(prompt_for_tool_use)

        # The response.content should ideally be the direct output of the tool if the LLM used it correctly.
        # This part might need refinement based on how the LLM formats its response when using tools.
        # It's expected that the LLM's response will include the structured dict from the tool.
        # We might need to parse response.content if it's not a direct dict.
        # For now, let's assume the LLM is configured to return the tool's output directly when appropriate.
        # This is a common pattern in agent frameworks but depends on the specific LLM and ADK version.

        # Let's assume the response.content *is* the dictionary from the tool.
        # This is an optimistic assumption. If the LLM wraps it in text, parsing will be needed.
        # A better approach for agents that *purely* validate via a tool and don't need LLM reasoning
        # for the validation itself, would be a simpler agent type or direct tool call if available.
        # Given LlmAgent, we rely on its tool-using capability.

        # For safety, let's try to directly access tool call results if ADK provides this:
        if response.tool_calls and response.tool_calls[0].name == "is_ticker_valid":
            return response.tool_calls[0].output

        # Fallback: if the LLM somehow put the dict string into content (less ideal)
        # This is a placeholder for more robust parsing if needed.
        # For now, we expect the tool_calls pathway.
        # If direct tool output is not in tool_calls, this agent will need more complex response parsing.
        return {"valid": False, "error": "LLM did not return tool output as expected."}


if __name__ == '__main__':
    # Example Usage (requires Google API key for LLM)
    # This part is for testing and might require API key setup (e.g., GOOGLE_API_KEY environment variable)
    try:
        agent = TickerValidationAgent()

        # Test with a valid ticker
        ticker_to_test = "AAPL"
        print(f"Validating ticker: {ticker_to_test}")
        result = agent.validate_ticker(ticker_to_test)
        print(f"Validation result for {ticker_to_test}: {result}")

        # Test with an invalid ticker
        invalid_ticker = "INVALIDTICKERXYZ"
        print(f"\nValidating ticker: {invalid_ticker}")
        result_invalid = agent.validate_ticker(invalid_ticker)
        print(f"Validation result for {invalid_ticker}: {result_invalid}")

        # Test with a ticker that might have info but is problematic
        problematic_ticker = "GOOG" # Sometimes yfinance needs specific suffix like GOOGL
        print(f"\nValidating ticker: {problematic_ticker}")
        result_problematic = agent.validate_ticker(problematic_ticker)
        print(f"Validation result for {problematic_ticker}: {result_problematic}")

    except Exception as e:
        print(f"An error occurred during example usage: {e}")
        print("Please ensure your Google API key is set up if you're running this example.")
