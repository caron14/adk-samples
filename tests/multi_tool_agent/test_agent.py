import os
import sys
import importlib
from unittest import mock

# Add agents directory to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Functions/objects to be imported from the module under test
# These are imported inside tests after mocks are set up.

# Expected tools for the agent
from agents.multi_tool_agent.util import (
    get_city_weather_candidates,
    get_city_timezones_candidates,
    get_current_time,
    get_weather,
)
expected_tools_list = [
    get_city_timezones_candidates,
    get_city_weather_candidates,
    get_weather,
    get_current_time,
]

# Test case for Agent initialization
@mock.patch.dict(os.environ, {
    "GOOGLE_GENAI_USE_VERTEXAI": "false", # Ensure setup_vertexai is not called by default
    "GOOGLE_CLOUD_PROJECT": "test-project",
    "GOOGLE_CLOUD_LOCATION": "test-region",
    "ROOT_AGENT_MODEL": "gemini-2.0-flash", # Use default from agent.py
    "SPECIFIC_AGENT_MODEL": "gemini-2.0-flash", # Expected by agent.py
}, clear=True) # clear=True ensures a clean env for this test
@mock.patch("agents.multi_tool_agent.agent.load_env") # To control env for agent.py's getenv calls
@mock.patch("agents.common.vertex_setup.vertexai.init") # Safeguard against real init
@mock.patch("google.adk.agents.Agent") # Patch Agent at its source
@mock.patch("agents.common.vertex_setup.setup_vertexai") # Patch setup_vertexai at its source
def test_agent_initialization(mock_source_setup_vertexai, mock_source_agent, mock_common_vertexai_init, mock_load_env_agent):
    # Import and reload the module under test INSIDE the test function, after mocks are set up.
    # This ensures that 'from ... import ...' statements in agent.py pick up the mocks.
    import agents.multi_tool_agent.agent as agent_module # Initial import

    # Reset mocks that would have been affected by the initial import.
    # The test focuses on the behavior during the reload with the specific environment.
    mock_source_agent.reset_mock()
    mock_source_setup_vertexai.reset_mock()
    mock_common_vertexai_init.reset_mock()
    mock_load_env_agent.reset_mock() # Though this is called from within agent_module, reset for clarity

    importlib.reload(agent_module) # Reload to execute module code with current test's mocks/env

    # Assert Agent (which is now mock_source_agent) was called once during the reload
    mock_source_agent.assert_called_once()

    # Get the arguments passed to the Agent constructor
    args, kwargs = mock_source_agent.call_args

    # Check specific arguments
    assert kwargs.get("name") == "weather_time_agent"
    assert kwargs.get("model") == "gemini-2.0-flash" # or os.getenv("ROOT_AGENT_MODEL")
    assert "Agent to answer questions about the time and weather" in kwargs.get("description")
    assert "You are a helpful agent who can answer user questions" in kwargs.get("instruction")

    # Check tools list (order might matter or might not, depending on implementation)
    # For now, check for presence and same length. If order is strict, use assertEqual.
    passed_tools = kwargs.get("tools")
    assert isinstance(passed_tools, list)
    assert len(passed_tools) == len(expected_tools_list)
    for tool in expected_tools_list:
        assert tool in passed_tools

    # Ensure setup_vertexai (which is mock_source_setup_vertexai) was NOT called
    mock_source_setup_vertexai.assert_not_called()
    # Ensure the actual vertexai.init was not called (already asserted by mock_common_vertexai_init if it's different)
    # but this is a good check if GOOGLE_GENAI_USE_VERTEXAI was true and setup_vertexai was called.
    mock_common_vertexai_init.assert_not_called()


# Test case for conditional call to setup_vertexai
@mock.patch("agents.common.vertex_setup.vertexai.init") # Safeguard, will be called by real setup_vertexai if not for outer mock
@mock.patch.dict(os.environ, {}, clear=True) # Start with a clean environment for each parameterization
@mock.patch("google.adk.agents.Agent") # Patch Agent at source, it's instantiated in agent.py
@mock.patch("agents.multi_tool_agent.agent.load_env") # To control env for agent.py
@mock.patch("agents.common.vertex_setup.setup_vertexai") # Patch setup_vertexai at source
def test_setup_vertexai_conditional_call(
    mock_source_common_setup_vertexai, # from @mock.patch("agents.common.vertex_setup.setup_vertexai")
    mock_load_env_agent,               # from @mock.patch("agents.multi_tool_agent.agent.load_env")
    mock_source_google_adk_agent,      # from @mock.patch("google.adk.agents.Agent")
    mock_common_vertexai_init_global   # from @mock.patch("agents.common.vertex_setup.vertexai.init")
):
    # Test when GOOGLE_GENAI_USE_VERTEXAI is true
    env_vars_true = {
        "GOOGLE_GENAI_USE_VERTEXAI": "true",
        "GOOGLE_CLOUD_PROJECT": "test-proj",
        "GOOGLE_CLOUD_LOCATION": "us-central1",
        "ROOT_AGENT_MODEL": "gemini-2.0-flash",
        "SPECIFIC_AGENT_MODEL": "gemini-2.0-flash"
    }
    with mock.patch.dict(os.environ, env_vars_true, clear=True):
        import agents.multi_tool_agent.agent as agent_module_true
        importlib.reload(agent_module_true)
        mock_source_common_setup_vertexai.assert_called_once_with(project="test-proj", region="us-central1")

    mock_source_common_setup_vertexai.reset_mock() # Reset for the next case

    # Test when GOOGLE_GENAI_USE_VERTEXAI is false
    env_vars_false = {
        "GOOGLE_GENAI_USE_VERTEXAI": "false",
        "GOOGLE_CLOUD_PROJECT": "test-proj-false",
        "GOOGLE_CLOUD_LOCATION": "us-central1",
        "ROOT_AGENT_MODEL": "gemini-2.0-flash",
        "SPECIFIC_AGENT_MODEL": "gemini-2.0-flash"
    }
    with mock.patch.dict(os.environ, env_vars_false, clear=True):
        import agents.multi_tool_agent.agent as agent_module_false
        importlib.reload(agent_module_false)
        mock_source_common_setup_vertexai.assert_not_called()

    mock_source_common_setup_vertexai.reset_mock() # Reset for the next case

    # Test when GOOGLE_GENAI_USE_VERTEXAI is not set
    env_vars_unset = {
        "GOOGLE_CLOUD_PROJECT": "test-proj-unset",
        "GOOGLE_CLOUD_LOCATION": "us-central1",
        "ROOT_AGENT_MODEL": "gemini-2.0-flash",
        "SPECIFIC_AGENT_MODEL": "gemini-2.0-flash"
    }
    current_env_copy = os.environ.copy() # Start from a clean copy due to clear=True on patch.dict
    current_env_copy.pop("GOOGLE_GENAI_USE_VERTEXAI", None)
    for k, v in env_vars_unset.items(): # Apply specific vars for this sub-test
        current_env_copy[k] = v

    with mock.patch.dict(os.environ, current_env_copy, clear=True):
        import agents.multi_tool_agent.agent as agent_module_unset
        importlib.reload(agent_module_unset)
        mock_source_common_setup_vertexai.assert_not_called()

    # mock_source_google_adk_agent is also reloaded each time, ensure it's called once per reload
    # This might need more granular checks if its calls vary per env scenario.
    # For now, the primary goal is setup_vertexai calls.
    # We also need to consider that Agent() is instantiated regardless of GOOGLE_GENAI_USE_VERTEXAI.
    # So mock_source_google_adk_agent will be called multiple times across reloads.
    # This test is primarily focused on setup_vertexai calls, so we might ignore Agent calls here or make them more specific.
