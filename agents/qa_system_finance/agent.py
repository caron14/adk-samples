import os

from google.adk.agents import LlmAgent

from agents.common.util import load_env
from agents.common.vertex_setup import setup_vertexai
from agents.qa_system_finance import (
    analyze_sentiment,
    search_news,
    summarize_financials,
    validate_ticker,
)

load_env()
GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = os.getenv("GOOGLE_CLOUD_LOCATION")
ROOT_AGENT_MODEL = os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash")
SPECIFIC_AGENT_MODEL = os.getenv("SPECIFIC_AGENT_MODEL", "gemini-2.0-flash")

if GOOGLE_GENAI_USE_VERTEXAI:
    setup_vertexai(project=PROJECT, region=REGION)

"""
Sub-Agents as a Tool
"""
ticker_validation_agent = LlmAgent(
    name="ticker_validator",
    model=SPECIFIC_AGENT_MODEL,
    instruction=(
        "Use the validate_ticker tool to check if the ticker provided by the "
        "user exists on Yahoo Finance. If the ticker is invalid, return an "
        "error message and stop the workflow."
    ),
    tools=[validate_ticker],
    output_key="validated_ticker",
)

news_retrieval_agent = LlmAgent(
    name="news_retriever",
    model=SPECIFIC_AGENT_MODEL,
    instruction=(
        "Retrieve recent news for the validated ticker during the specified "
        "week using search_news. Provide a list of headlines and short "
        "summaries."
    ),
    tools=[search_news],
)

financial_summary_agent = LlmAgent(
    name="financial_summary",
    model=SPECIFIC_AGENT_MODEL,
    instruction=(
        "Gather recent earnings or financial statement information using "
        "summarize_financials for the validated ticker."
    ),
    tools=[summarize_financials],
)

sentiment_agent = LlmAgent(
    name="sentiment_analyzer",
    model=SPECIFIC_AGENT_MODEL,
    instruction=(
        "Evaluate the sentiment of the news articles using analyze_sentiment."
    ),
    tools=[analyze_sentiment],
)

"""
Supervisor Agent
"""
root_agent = LlmAgent(
    name="finance_supervisor",
    model=ROOT_AGENT_MODEL,
    description="Supervisor agent for stock price movement analysis.",
    instruction=(
        "You converse with the user to obtain a stock ticker and week. "
        "Then coordinate sub-agents to validate the ticker, collect news, "
        "summarize financial data and analyze sentiment. Provide a concise "
        "weekly report of potential reasons for stock price movements."
    ),
    sub_agents=[
        ticker_validation_agent,
        news_retrieval_agent,
        financial_summary_agent,
        sentiment_agent,
    ],
)
