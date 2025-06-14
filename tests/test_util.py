import importlib.util
import os
from pathlib import Path

util_path = (
    Path(__file__).resolve().parents[1]
    / "agents"
    / "multi_tool_agent"
    / "util.py"
)
spec = importlib.util.spec_from_file_location("multi_tool_util", util_path)
util = importlib.util.module_from_spec(spec)
spec.loader.exec_module(util)


def test_get_weather_known_city():
    result = util.get_weather("Tokyo")
    assert result["status"] == "success"
    assert "Tokyo" in result["report"]


def test_get_weather_unknown_city():
    result = util.get_weather("Atlantis")
    assert result["status"] == "error"


def test_get_current_time_known_city():
    result = util.get_current_time("New York")
    assert result["status"] == "success"
    assert "New York" in result["report"]


def test_get_city_timezones_candidates_contains_tokyo():
    assert "tokyo" in util.get_city_timezones_candidates()


def test_get_city_weather_candidates_contains_tokyo():
    assert "tokyo" in util.get_city_weather_candidates()
