# ADK Sample Agents Repository

This repository provides a collection of sample AI agents and reference implementations for both Python and Java. It is designed to help developers understand, customize, and deploy various agent-based solutions using the Agent Development Kit (ADK). Each agent is organized as an independent project with its own documentation, code, and deployment resources. Common utilities and shared modules are also included for reuse and extension.

## Repository Structure

- `agents/`
  - Common agent-related code and utilities.
- `common/`
  - Shared utilities and setup scripts used across agents.
- Root files
  - `pyproject.toml`, `README.md`, `uv.lock`, etc. — project-wide configuration and documentation files.

## Set up the model

Gemini - Google Cloud Vertex AI
1. You need an existing Google Cloud account and a project.
- Set up a Google Cloud project
- Set up the gcloud CLI
- Authenticate to Google Cloud, from the terminal by running gcloud auth login.
- Enable the Vertex AI API.

2. When using Python, open the .env file. Copy-paste the following code and update the project ID and location.

```env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=LOCATION
```

## Reference:
- https://google.github.io/adk-docs/
