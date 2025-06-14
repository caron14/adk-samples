# Financial QA System Agent

## Overview

This project is a Python-based agent system designed to gather financial information about a publicly traded company for a specified period. It fetches stock prices, relevant financial reports, company-specific news, and general market news. The system is orchestrated by a supervisor agent that interacts with the user and coordinates various worker agents to collect and present the data in a consolidated JSON format.

## Features

-   **Interactive Input**: Prompts the user for a stock ticker symbol and an analysis period (in weeks offset from the current week).
-   **Ticker Validation**: Checks if the provided ticker symbol is valid using `yfinance`.
-   **Stock Price Retrieval**: Fetches daily historical stock prices (Open, Close, High, Low, Volume) for the specified week using `yfinance`.
-   **Financial Report Search**: Searches for links to annual and earnings reports using DuckDuckGo search.
-   **Company News Search**: Searches for company-specific news articles for the period using DuckDuckGo search.
-   **Market News Search**: Searches for general market news and economic trends during the period using DuckDuckGo search.
-   **Consolidated Output**: Presents all gathered information in a structured JSON output, including a generated overall summary.

## Project Structure

The project is organized within the `agents/qa_system_finance/` directory with the following main components:

-   `main.py`: The main entry point to run the system.
-   `requirements.txt`: Lists Python package dependencies.
-   `supervisor/`: Contains the `SupervisorAgent` that orchestrates the workflow.
-   `workers/`: Contains specialized worker agents for specific tasks:
    -   `stock_price_agent.py`: Fetches stock prices.
    -   `financial_report_agent.py`: Finds financial reports.
    -   `company_news_agent.py`: Finds company news.
    -   `market_news_agent.py`: Finds market news.
    -   `ticker_validation_agent.py`: Validates ticker symbols.
-   `utils/`: Contains utility functions, like `date_utils.py` for date calculations.
-   `tests/`: Contains unit tests for the system's components.
-   `README.md`: This file.

## Installation

1.  **Clone the repository** (if applicable, or ensure you have the `agents` directory).

2.  **Navigate to the project directory**:
    ```bash
    cd path/to/your/agents/qa_system_finance
    # Or ensure your Python execution path is set up to find the 'agents' package
    ```

3.  **Install dependencies**:
    It's recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
    If you are running within a larger project structure that might have a top-level `agents/__init__.py` causing import issues with `vertexai` during testing or execution (if `vertexai` is not used by this specific sub-project but is imported at top-level), you might need to install it:
    ```bash
    pip install google-cloud-aiplatform
    ```

## How to Run

Once dependencies are installed, you can run the system using:

```bash
python3 -m agents.qa_system_finance.main
```
Or, if your `PYTHONPATH` is set up to include the directory containing the `agents` package:
```bash
python3 agents/qa_system_finance/main.py
```

The system will then prompt you to enter a ticker symbol and the desired analysis period. After processing, it will print the consolidated financial data as a JSON object to the console.

## Running Tests

To run the unit tests:

```bash
python3 -m unittest discover agents/qa_system_finance/tests
```
Ensure all dependencies, including those for testing (like `unittest.mock`), are available in your environment.
The tests ensure that individual components (date utilities, worker agents, supervisor logic) function as expected.
