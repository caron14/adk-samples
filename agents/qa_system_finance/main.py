import asyncio
import sys
from agents.qa_system_finance.supervisor_agent import SupervisorAgent
from agents.qa_system_finance.ticker_validation_agent import TickerValidationAgent
from agents.qa_system_finance.news_retrieval_agent import NewsRetrievalAgent
from adk.graph import Graph # For potential future use if we convert to a graph-based execution

# ADK components often require API keys to be set as environment variables.
# e.g., GOOGLE_API_KEY for Gemini models.
# Ensure these are set in your environment before running.

async def main_cli():
    """
    Command-line interface to interact with the Stock Analysis Supervisor Agent.
    """
    print("Initializing Stock Analysis Agent...")

    # Initialize sub-agents
    # These agents might have their own LLM configurations or use defaults.
    try:
        ticker_validator = TickerValidationAgent()
        news_retriever = NewsRetrievalAgent()
    except Exception as e:
        print(f"Error initializing sub-agents: {e}")
        print("Please ensure your ADK setup and API keys (e.g., GOOGLE_API_KEY) are correct.")
        return

    # Initialize SupervisorAgent with its dependencies
    supervisor = SupervisorAgent(
        ticker_validation_agent=ticker_validator,
        news_retrieval_agent=news_retriever
    )

    print("Stock Analysis Agent ready. Type 'quit' to exit.")

    # Initial message from the agent (e.g., asking for a ticker)
    # The supervisor's process_user_request is designed to be called iteratively.
    # An initial empty call can trigger the first prompt.
    try:
        initial_agent_response = await supervisor.process_user_request("") # Or a specific greeting
        print(f"Agent: {initial_agent_response}")
    except Exception as e:
        print(f"Error during initial agent processing: {e}")
        print("This might be due to LLM API issues or configuration problems.")
        return

    while True:
        try:
            user_input = await asyncio.to_thread(input, "You: ") # Non-blocking input for async
        except RuntimeError: # Fallback for environments where to_thread might not work as expected
            user_input = input("You: ")


        if user_input.lower().strip() == 'quit':
            print("Exiting agent.")
            break

        if not user_input.strip():
            continue

        try:
            agent_response = await supervisor.process_user_request(user_input)
            print(f"Agent: {agent_response}")

            # Check if the conversation cycle is complete to reset for a new query
            # This logic is based on the supervisor's state handling.
            current_state = await supervisor.get_state()
            # If results are shown or a terminal error occurred, and the agent is not asking a follow-up question for the same query
            if (current_state.news_results is not None or \
                (current_state.error_message is not None and "Please provide a valid ticker" not in agent_response)) and \
                not agent_response.endswith(supervisor.ask_for_week_prompt) and \
                not agent_response.startswith("Sorry, I didn't understand the week input"):

                print("Agent: Conversation cycle complete. Ready for a new query or type 'quit'.")
                await supervisor.clear_state() # Reset for the next independent query
                # Optional: automatically show the initial prompt again
                # initial_agent_response_new_query = await supervisor.process_user_request("")
                # print(f"Agent: {initial_agent_response_new_query}")


        except Exception as e:
            print(f"An error occurred: {e}")
            print("Restarting conversation flow with the agent due to an unexpected error.")
            await supervisor.clear_state() # Clear state on error
            try:
                error_recovery_prompt = await supervisor.process_user_request("") # Get initial prompt
                print(f"Agent: {error_recovery_prompt}")
            except Exception as e_recovery:
                print(f"Critical error during recovery: {e_recovery}. Exiting.")
                break


if __name__ == "__main__":
    # Ensure GOOGLE_API_KEY is set in your environment
    # For example: export GOOGLE_API_KEY="your_api_key_here"

    # Fix for asyncio on Windows from Python 3.8+
    if sys.platform == "win32" and sys.version_info >= (3, 8, 0):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(main_cli())
    except KeyboardInterrupt:
        print("\nExiting application...")
    except Exception as e:
        print(f"Unhandled error in main: {e}")
