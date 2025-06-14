import sys
from adk.agent import LlmAgent, AgentState
from adk.config import CommonAgentConfig
from adk.message import MessageScope, ChatMessage
from agents.qa_system_finance.ticker_validation_agent import TickerValidationAgent
from agents.qa_system_finance.news_retrieval_agent import NewsRetrievalAgent
from datetime import datetime, timedelta

class StockAnalysisSupervisorState(AgentState):
    ticker: str | None = None
    ticker_valid: bool = False
    ticker_info: str | None = None
    week_monday_str: str | None = None # YYYY-MM-DD
    news_results: dict | None = None
    error_message: str | None = None

class SupervisorAgent(LlmAgent[StockAnalysisSupervisorState]):
    def __init__(
        self,
        ticker_validation_agent: TickerValidationAgent,
        news_retrieval_agent: NewsRetrievalAgent
    ):
        super().__init__(
            state_type=StockAnalysisSupervisorState,
            config=CommonAgentConfig(llm_config_template_path=None) # Default Gemini Pro
        )
        self.ticker_validation_agent = ticker_validation_agent
        self.news_retrieval_agent = news_retrieval_agent

        # Define initial prompts or conversation starters if needed
        self.initial_prompt = "Hello! I can help you analyze stock price fluctuations. Which stock ticker would you like to analyze?"
        self.ask_for_week_prompt = "Which week are you interested in? Please provide a date within that week (e.g., 'last Monday', '2023-10-16'), or 'this week', 'last week'."

    async def _normalize_week_input(self, week_input: str) -> str | None:
        """
        Normalizes various week inputs to the Monday of that week in 'YYYY-MM-DD' format.
        Returns None if input is not understood.
        """
        today = datetime.now().date()
        week_input_lower = week_input.lower().strip()

        if "this week" in week_input_lower:
            monday = today - timedelta(days=today.weekday())
            return monday.strftime("%Y-%m-%d")
        elif "last week" in week_input_lower:
            monday = today - timedelta(days=today.weekday() + 7)
            return monday.strftime("%Y-%m-%d")
        elif "next week" in week_input_lower: # Added for completeness, though not typical for historical analysis
            monday = today - timedelta(days=today.weekday() - 7)
            return monday.strftime("%Y-%m-%d")
        else:
            try:
                # Try to parse as a specific date
                input_date = datetime.strptime(week_input_lower, "%Y-%m-%d").date()
                monday = input_date - timedelta(days=input_date.weekday())
                return monday.strftime("%Y-%m-%d")
            except ValueError:
                # Could add more sophisticated date parsing here (e.g., "October 5th", "next monday")
                # For now, keep it simple. The LLM itself might also help guide user for re-entry.
                # We can also use an LLM call to parse the date if native Python fails.
                # For this iteration, we'll rely on simple parsing or LLM re-prompt.

                # Attempt LLM based date normalization as a fallback
                prompt = f"Convert the following user input into a specific Monday date (YYYY-MM-DD) of the described week: '{week_input}'. If you can determine the Monday, reply with only the date string. Otherwise, reply with 'Error: Cannot determine date.'"
                response_msg = await self.get_llm_response(prompt) # Assumes get_llm_response is available or self.chat()

                llm_response_text = response_msg.content.strip()
                try:
                    # Check if LLM returned a valid date string
                    datetime.strptime(llm_response_text, "%Y-%m-%d")
                    return llm_response_text # It's a valid date string
                except ValueError:
                    return None # LLM also failed

    async def process_user_request(self, user_query: str) -> str:
        """
        Main entry point to process a user's request through the workflow.
        This is a simplified flow for now. ADK's `run` or `arun` with graph definition
        would be the standard way for complex flows.
        This method simulates a sequential flow controlled by the supervisor's logic.
        """
        # Initialize or retrieve current state
        state = await self.get_state() # Essential for ADK agents

        if state.ticker is None:
            # If ticker is not in state, assume user_query is the ticker or contains it.
            # A more robust approach would be to have the LLM extract the ticker.
            # For now, let's assume user_query IS the ticker if state.ticker is None.
            # Or, if it's the first interaction, user_query might be a general greeting.

            # Let's use an LLM call to extract ticker from the initial query
            # or confirm if the query is a ticker.
            extract_ticker_prompt = f"The user said: '{user_query}'. Is this a stock ticker? If yes, return only the ticker symbol. If no, or if it's a greeting/question, ask them for the ticker symbol they are interested in."
            llm_response_for_ticker = await self.get_llm_response(extract_ticker_prompt)
            potential_ticker = llm_response_for_ticker.content.strip().upper()

            # Simplistic check: if it looks like a ticker (e.g. < 5 chars, alphanumeric)
            # A proper check would involve trying to validate it.
            if len(potential_ticker) > 0 and len(potential_ticker) < 6 and potential_ticker.isalnum() and not any(char in potential_ticker for char in " ?!,."):
                state.ticker = potential_ticker
            else:
                # LLM's response was not a ticker, so it should be a question asking for one.
                return potential_ticker # Return the LLM's question to the user.


        if state.ticker and not state.ticker_valid:
            # We have a ticker, now validate it.
            validation_result = self.ticker_validation_agent.validate_ticker(state.ticker)
            if validation_result.get("valid"):
                state.ticker_valid = True
                state.ticker_info = validation_result.get("info", state.ticker)
                await self.set_state(state) # Save updated state
                # Now ask for the week
                return self.ask_for_week_prompt
            else:
                error_msg = validation_result.get("error", "Invalid ticker symbol.")
                state.error_message = error_msg
                state.ticker = None # Reset ticker so user can provide a new one
                await self.set_state(state)
                return f"Error: {error_msg}. Please provide a valid ticker symbol."

        if state.ticker_valid and state.week_monday_str is None:
            # Ticker is valid, now we need the week. Assume user_query is the week input.
            normalized_week = await self._normalize_week_input(user_query)
            if normalized_week:
                state.week_monday_str = normalized_week
                await self.set_state(state)
                # Proceed to news retrieval
            else:
                # Could not normalize week input
                return f"Sorry, I didn't understand the week input '{user_query}'. Please try 'YYYY-MM-DD', 'last week', or 'this week'."

        if state.ticker_valid and state.week_monday_str and state.news_results is None:
            # We have a valid ticker and a normalized week, get news
            news_result = self.news_retrieval_agent.get_news(state.ticker, state.week_monday_str)
            state.news_results = news_result
            await self.set_state(state)

            if "error" in news_result:
                return f"Error retrieving news: {news_result['error']}"
            elif not news_result.get("news_items"):
                return f"No news found for {state.ticker_info or state.ticker} for the week of {state.week_monday_str}."
            else:
                # Format and return news
                # This part can be enhanced by an LLM to summarize the news.
                response_lines = [f"Found {len(news_result['news_items'])} news items for {state.ticker_info or state.ticker} (week of {state.week_monday_str}):"]
                for item in news_result["news_items"][:5]: # Show top 5
                    response_lines.append(f"- Title: {item.get('title', 'N/A')}")
                    response_lines.append(f"  Snippet: {item.get('body', 'N/A')}")
                    response_lines.append(f"  URL: {item.get('url', 'N/A')}")

                # Clear state for next request or manage conversation turns more explicitly
                await self.clear_state() # Example: clear state after providing results
                return "\n".join(response_lines)

        # Fallback or initial prompt if no specific state is matched
        # This part of the logic might need refinement based on how conversations are managed.
        # If state.ticker is None, it means we need to ask for it.
        if state.ticker is None:
            return self.initial_prompt

        return "I'm not sure how to proceed. Could you clarify your request?"


    async def get_llm_response(self, prompt: str) -> ChatMessage:
        """Helper to get a direct LLM response (not using tools)."""
        # This uses the agent's own chat method, but ensures no tools are expected for this call.
        # The ADK might have a more direct way to call the LLM without tool processing.
        # For now, we use self.chat() and rely on the prompt to guide the LLM.
        # A specific method like `self.llm.generate_text()` would be ideal if available.
        # This is a placeholder for how an LlmAgent might query its LLM for simple text generation.

        # The base LlmAgent's chat method is designed for tool use.
        # For non-tool prompts, we might need to ensure it behaves as a simple text completion.
        # Let's assume self.chat() can handle simple Q&A if no tools are matched.

        # Create a user message
        user_message = ChatMessage(content=prompt, scope=MessageScope.USER)

        # Call the LLM. This is a simplified call.
        # The actual `self.chat` or a similar method in ADK would handle history, etc.
        # For this example, let's assume a method like this exists or self.chat() is adaptable.
        # If `self.chat` is strictly for tool-enabled conversation turns, this needs adjustment.
        # The `LlmAgent` in ADK is tool-centric. For pure LLM generation without tool context,
        # one might use the LLM client directly (e.g., `self.llm_client.generate_text(...)`).
        # Let's assume for now `self.chat` can be used carefully for this.

        # This is a conceptual representation. The actual implementation would use ADK's LLM invocation.
        # This might be:
        # response = await self.llm.generate_text_async(prompt=prompt)
        # return ChatMessage(content=response.text, scope=MessageScope.MODEL)
        # For now, using self.chat as a placeholder for LLM interaction.

        # The `chat` method of `LlmAgent` expects a string and returns a `ChatMessage`.
        # It internally handles history and tool calls.
        # For a simple LLM text generation, the prompt should be crafted so the LLM doesn't try to use tools.
        return await self.chat(prompt) # This may not be ideal if chat always tries tool matching.


# Example usage (conceptual, as it requires an async event loop and proper setup)
if __name__ == '__main__':
    import asyncio

    async def main():
        # This is a very simplified setup for illustration.
        # In a real ADK app, agents are typically part of a graph or managed by a framework.

        # Initialize sub-agents
        ticker_validator = TickerValidationAgent()
        news_retriever = NewsRetrievalAgent()

        # Initialize SupervisorAgent
        supervisor = SupervisorAgent(
            ticker_validation_agent=ticker_validator,
            news_retrieval_agent=news_retriever
        )

        print("SupervisorAgent Example (Type 'quit' to exit)")
        print(await supervisor.process_user_request("")) # Initial greeting / prompt for ticker

        while True:
            user_input = input("You: ")
            if user_input.lower() == 'quit':
                break

            if not user_input.strip():
                continue

            response = await supervisor.process_user_request(user_input)
            print(f"Agent: {response}")

            # Check if the conversation should end based on state or response
            current_state = await supervisor.get_state()
            if current_state.news_results is not None or current_state.error_message is not None:
                if not response.endswith("Please provide a valid ticker symbol.") and not response.endswith(supervisor.ask_for_week_prompt):
                    print("Supervisor: Restarting conversation for new query.")
                    await supervisor.clear_state() # Clears state for next independent query
                    print(await supervisor.process_user_request("")) # Initial greeting

    if sys.platform == "win32" and sys.version_info >= (3, 8, 0): # Specific fix for asyncio on Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # This example requires API keys and ADK setup to run fully.
    # asyncio.run(main()) # Commented out as it won't run directly in this subtask environment
    print("SupervisorAgent structure defined. Example main() for illustration purposes.")
    print("Note: Full execution of this example requires an async environment and ADK setup.")
    print("The process_user_request method outlines the primary logic flow.")
