"""
Main entry point for the Financial QA System.

This script initializes and runs the supervisor agent, which orchestrates various worker
agents to gather financial data, news, and stock prices for a user-specified company
and period. The final consolidated information is then printed as a JSON object.
"""
import json # For printing the final output
from agents.qa_system_finance.supervisor.supervisor_agent import SupervisorAgent
# from dotenv import load_dotenv # Example if .env is used
# import os # Example if .env is used

if __name__ == "__main__":
    # This is the main entry point for the QA System.
    # It creates a SupervisorAgent instance and starts its process.

    # Example: Load environment variables if a .env file exists (e.g., for API keys)
    # if os.path.exists(".env"):
    #     load_dotenv()
    #     print("Loaded environment variables from .env")
    # else:
    #     print(".env file not found, skipping dotenv loading.")

    print("Starting Financial QA System...")

    supervisor = SupervisorAgent()
    try:
        # The run method now returns the consolidated data
        output = supervisor.run()

        if output:
            # Print the final JSON output to the console
            print("\n=== FINAL OUTPUT ===")
            print(json.dumps(output, indent=2, ensure_ascii=False))
            print("====================")
        else:
            print("Supervisor did not produce an output.")

    except KeyboardInterrupt:
        print("\nQA System interrupted by user. Exiting.")
    except Exception as e:
        # Catch any other unexpected errors during the supervisor's run
        print(f"An unexpected error occurred in the main execution: {e}")
        # In a production system, this would be logged more formally.

    print("Financial QA System finished.")
