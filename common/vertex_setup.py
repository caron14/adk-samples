import os
import sys

import vertexai
from vertexai.generative_models import GenerativeModel

REPO_PATH = os.path.realpath(os.path.dirname(os.path.realpath("__file__")))
sys.path.append(REPO_PATH)
from common import load_env

load_env()
GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = os.getenv("GOOGLE_CLOUD_LOCATION")
ROOT_AGENT_MODEL = os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash")
SPECIFIC_AGENT_MODEL = os.getenv("SPECIFIC_AGENT_MODEL", "gemini-2.0-flash")


def setup_vertexai(project: str, region: str) -> None:
    """Setup Vertex AI for the agent."""
    os.system("gcloud config set project " + project)
    os.system("gcloud config set ai/region " + region)
    # os.system("gcloud auth application-default login")

    print("Using default credentials for Vertex AI.")
    vertexai.init(
        project=project,
        location=region,
        credentials=None,  # Use default credentials
    )
    print("Vertex AI initialized.\n\n")


if __name__ == "__main__":
    print("The test started setting up Vertex AI...")
    setup_vertexai(project=PROJECT, region=REGION)
    print("Vertex AI initialized.")

    # Test the GenerativeModel with a sample query
    model = GenerativeModel(ROOT_AGENT_MODEL)
    response = model.generate_content(
        "What's a good name for a flower shop that specializes in selling bouquets of dried flowers?"
    )
    print(response.text)
