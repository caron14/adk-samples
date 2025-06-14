"""Stock price analysis agent workflow using Google ADK."""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from .ticker_validation import validate_ticker
from .news_retrieval import search_news
from .financial_summary import get_financial_summary
from .sentiment_analysis import analyze_sentiment

# Tools wrapping the utility functions
validate_ticker_tool = FunctionTool(func=validate_ticker)
news_retrieval_tool = FunctionTool(func=search_news)
financial_summary_tool = FunctionTool(func=get_financial_summary)
sentiment_analysis_tool = FunctionTool(func=analyze_sentiment)

# Sub agents
ticker_validation_agent = LlmAgent(
    name="TickerValidationAgent",
    model="gemini-2.0-pro",
    instruction=(
        "Validate the given stock ticker using the provided tool. "
        "Return an error if the ticker is invalid."
    ),
    tools=[validate_ticker_tool],
)

news_retrieval_agent = LlmAgent(
    name="NewsRetrievalAgent",
    model="gemini-2.0-pro",
    instruction=(
        "Search recent news for the ticker and the specified week using the "
        "search_news tool. Summarize the headlines."
    ),
    tools=[news_retrieval_tool],
)

financial_summary_agent = LlmAgent(
    name="FinancialSummaryAgent",
    model="gemini-2.0-pro",
    instruction=(
        "Fetch financial results such as earnings using the provided tool."
    ),
    tools=[financial_summary_tool],
)

sentiment_analysis_agent = LlmAgent(
    name="SentimentAnalysisAgent",
    model="gemini-2.0-pro",
    instruction=(
        "Analyze sentiment of text using the analyze_sentiment tool and "
        "report whether it is positive, negative, or neutral."
    ),
    tools=[sentiment_analysis_tool],
)

# Supervisor agent orchestrating the workflow
supervisor_agent = LlmAgent(
    name="StockSupervisorAgent",
    model="gemini-2.0-pro",
    instruction=(
        "You are a supervisor agent that coordinates sub agents to analyze "
        "why a stock moved during a given week."
    ),
    sub_agents=[
        ticker_validation_agent,
        news_retrieval_agent,
        financial_summary_agent,
        sentiment_analysis_agent,
    ],
)
