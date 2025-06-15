"""
Ref.
    - https://google.github.io/adk-docs/agents/models/#using-hosted-tuned-models-on-vertex-ai
"""

import os

from dotenv import find_dotenv, load_dotenv

import vertexai
from google.adk.agents import LlmAgent

def load_env() -> None:
    """
    Load environment variables from .env file.

    Searches for .env file in parent directories and loads
    environment variables from it.
    """
    _ = load_dotenv(find_dotenv())

load_env()
GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = os.getenv("GOOGLE_CLOUD_LOCATION")
ROOT_AGENT_MODEL = os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash")
SPECIFIC_AGENT_MODEL = os.getenv("SPECIFIC_AGENT_MODEL", "gemini-2.0-flash")

# Endpoint of the deployed model on Vertex AI(online prediction)
ENDPOINT = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_MODEL_ENDPOINT_ID"

def setup_vertexai(project: str, region: str) -> None:
    # Setup Vertex AI Environment
    os.system("gcloud config set project " + project)
    os.system("gcloud config set ai/region " + region)
    os.system("gcloud auth application-default login")

    print("Using default credentials for Vertex AI.")
    vertexai.init(
        project=project,
        location=region,
        credentials=None,  # Use default credentials
        api_endpoint=None,  # Use default API endpoint
    )
    print("Vertex AI initialized.\n\n")

def say_hello() -> str:
    """
    A simple tool that returns a greeting message.
    """
    return "Hello! How are you today?"

root_agent = LlmAgent(
    name="greeting_agent",
    model="gemini-2.0-flash",
    # model=ENDPOINT,
    description=(
        "Agent to say hello to the user"
    ),
    instruction=(
        "You are an agent who has a great personality. You can say hello to the user."
    ),
    tools=[
        say_hello,
    ],
)

