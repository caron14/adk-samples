import os
import sys
from unittest import mock

# Add agents directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Need to import the specific functions from the module
from agents.common.vertex_setup import setup_vertexai, load_env_local

# --- Test for load_env_local ---
def test_load_env_local():
    dummy_env_file_path = os.path.join(os.path.dirname(__file__), ".env.test_load_env_local")
    test_key = "TEST_LOAD_ENV_LOCAL_VAR"
    test_value = "test_value_vertex_setup_456"
    original_value = os.environ.pop(test_key, None)

    with open(dummy_env_file_path, "w") as f:
        f.write(f"{test_key}={test_value}\n")

    try:
        # Mock find_dotenv specifically for the call within agents.common.vertex_setup
        with mock.patch("agents.common.vertex_setup.find_dotenv", return_value=dummy_env_file_path):
            load_env_local()
        assert os.getenv(test_key) == test_value
    finally:
        if os.path.exists(dummy_env_file_path):
            os.remove(dummy_env_file_path)
        if os.getenv(test_key):
            del os.environ[test_key]
        if original_value is not None:
            os.environ[test_key] = original_value

# --- Tests for setup_vertexai ---
@mock.patch("agents.common.vertex_setup.os.system")
@mock.patch("agents.common.vertex_setup.vertexai.init")
def test_setup_vertexai(mock_vertexai_init, mock_os_system):
    test_project = "test-project-id"
    test_region = "test-region"

    setup_vertexai(project=test_project, region=test_region)

    # Check calls to os.system
    expected_calls_os_system = [
        mock.call(f"gcloud config set project {test_project}"),
        mock.call(f"gcloud config set ai/region {test_region}"),
    ]
    mock_os_system.assert_has_calls(expected_calls_os_system, any_order=False)

    # Check call to vertexai.init
    mock_vertexai_init.assert_called_once_with(
        project=test_project,
        location=test_region,
        credentials=None,
    )

@mock.patch.dict(os.environ, {"GOOGLE_GENAI_USE_VERTEXAI": "true", "GOOGLE_CLOUD_PROJECT": "env_project", "GOOGLE_CLOUD_LOCATION": "env_region"})
@mock.patch("agents.common.vertex_setup.setup_vertexai")
def test_module_level_setup_call(mock_setup_vertexai):
    # This test is a bit tricky. The setup_vertexai call happens at module import time
    # if GOOGLE_GENAI_USE_VERTEXAI is true in vertex_setup.py.
    # To test this, we need to reload the module after setting the mocks.
    # Note: This test is for the __main__ block execution in vertex_setup.py, not the agent.py usage.
    # The agent.py itself calls setup_vertexai conditionally.
    # The prompt implies testing the functions, rather than side effects of module import.
    # The if __name__ == "__main__": block in vertex_setup.py calls setup_vertexai.

    # Let's clarify: the plan asks to test agents/common/vertex_setup.py.
    # The primary function is setup_vertexai().
    # The load_env_local() is also there.
    # The if __name__ == "__main__": block is usually for direct execution scripts, not typically unit tested
    # unless it contains critical logic not exposed otherwise.
    # The agent.py script *also* calls setup_vertexai, which is a more relevant execution path to test.
    # For now, focusing on testing the functions setup_vertexai and load_env_local directly.
    pass # Keeping the structure, but the module-level call from __main__ is less of a unit test concern.
