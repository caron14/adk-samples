# ADK Sample Agents Repository

This repository provides a collection of sample AI agents and reference implementations for both Python and Java. It is designed to help developers understand, customize, and deploy various agent-based solutions using the Agent Development Kit (ADK). Each agent is organized as an independent project with its own documentation, code, and deployment resources. Common utilities and shared modules are also included for reuse and extension.

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/caron14/adk-samples.git
```

2. Navigate to the project directory:
```bash
cd adk-samples
```

3. Install the required dependencies:
```bash
uv sync
```

The dependency for development can be installed:
```bash
uv sync --extra dev
```

4. Set up the environment variables:
   Create a `.env` file in the root directory and add the following variables:
   ```env
   GOOGLE_GENAI_USE_VERTEXAI=TRUE
   GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
   GOOGLE_CLOUD_LOCATION=LOCATION
   ```
5. If you are using Google Cloud Vertex AI, ensure you have the necessary permissions and have set up your Google Cloud project as described in the [Set up the model](#set-up-the-model) section below.
   If you are using a different model, adjust the environment variables accordingly.
   For example, if you are using OpenAI, you might need to set `OPENAI_API_KEY` and other relevant variables.
   ```env
    ROOT_AGENT_MODEL='your-root-agent-model-id' # ex. 'gemini-2.0-flash-lite-001'
    SPECIFIC_AGENT_MODEL='your-specific-agent-model-id' # ex. 'gemini-2.0-flash-lite-001'
    ```
6. Run the agent:
   ```bash
   python -m agents.<agent_name>
   ```

## Development Tools
pylint/balck/isort/mypy/pytest
```bash
uv run pylint $(git ls-files '*.py')
uv run black .
uv run isort .
uv run mypy .
uv run pytest  
```

Test the black formatter to ensure the CI pipeline will pass:
```bash
uv run black --check --diff .
```

# Test by Pytest
```bash
uv run pytest -q
```

## Reference:
- https://google.github.io/adk-docs/

**Prompting Guide by OpenAI**
- [GPT4.1 Prompting Guide](https://media.licdn.com/dms/document/media/v2/D4E1FAQFJukaW0z5PDQ/feedshare-document-pdf-analyzed/B4EZZFAKJ_HUAY-/0/1744914403183?e=1751500800&v=beta&t=x5kdIh02AnRy7Uom2qAjVGT7lUree73zxJqRU7P9B3k)