import os
import sys

from google.adk.agents import Agent

REPO_PATH = os.path.realpath(os.path.dirname(os.path.realpath("__file__")))
sys.path.append(REPO_PATH)

from agents.multi_tool_agent import (
    get_current_time,
    get_weather,
)
from common import (
    load_env,
    setup_vertexai,
)

load_env()
GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = os.getenv("GOOGLE_CLOUD_LOCATION")
ROOT_AGENT_MODEL = os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash")
SPECIFIC_AGENT_MODEL = os.getenv("SPECIFIC_AGENT_MODEL", "gemini-2.0-flash")

# print(f"GOOGLE_GENAI_USE_VERTEXAI: {GOOGLE_GENAI_USE_VERTEXAI}")
# print(f"PROJECT: {PROJECT}")
# print(f"REGION: {REGION}")
# print(f"ROOT_AGENT_MODEL: {ROOT_AGENT_MODEL}")
# print(f"SPECIFIC_AGENT_MODEL: {SPECIFIC_AGENT_MODEL}")

# Setup Vertex AI
if GOOGLE_GENAI_USE_VERTEXAI:
    print("Setting up Vertex AI...")
    setup_vertexai(
        project=PROJECT,
        region=REGION,
    )

root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[get_weather, get_current_time],
)
