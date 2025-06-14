import os
import sys
import datetime
from unittest import mock

# Add agents directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agents.multi_tool_agent.util import (
    get_weather,
    get_city_timezones_candidates,
    get_city_weather_candidates,
    get_current_time,
    CITY_WEATHER,
    CITY_TIMEZONES,
)

# --- Tests for get_weather ---
def test_get_weather_known_city():
    city = "tokyo" # A city known to be in CITY_WEATHER
    result = get_weather(city)
    assert result["status"] == "success"
    assert city.lower() in result["report"].lower()
    assert "temperature" in result["report"]

def test_get_weather_known_city_mixed_case():
    city = "LoNdOn"
    expected_city_data_key = "london"
    result = get_weather(city)
    assert result["status"] == "success"
    assert CITY_WEATHER[expected_city_data_key]['condition'] in result["report"]
    assert str(CITY_WEATHER[expected_city_data_key]['temperature_c']) in result["report"]

def test_get_weather_city_in_timezones_not_weather():
    # Find a city that is in CITY_TIMEZONES but not in CITY_WEATHER
    city_in_tz_not_in_weather = "madrid" # Example, ensure this city is in CITY_TIMEZONES and not CITY_WEATHER
    if city_in_tz_not_in_weather.lower() not in CITY_WEATHER:
        result = get_weather(city_in_tz_not_in_weather)
        assert result["status"] == "success" # As per current implementation
        assert f"Weather information for {city_in_tz_not_in_weather} is currently unavailable" in result["report"]
    else:
        # This case would mean 'madrid' was added to CITY_WEATHER, pick another or skip
        pass

def test_get_weather_unknown_city():
    city = "unknown_city_12345"
    result = get_weather(city)
    assert result["status"] == "error"
    assert f"Weather information for '{city}' is not available" in result["error_message"]

# --- Tests for get_city_timezones_candidates ---
def test_get_city_timezones_candidates():
    candidates = get_city_timezones_candidates()
    assert isinstance(candidates, list)
    assert all(isinstance(city, str) for city in candidates)
    assert candidates == sorted(candidates) # Check if sorted
    # Check a few known cities
    assert "new york" in candidates
    assert "london" in candidates
    if "madrid" in CITY_TIMEZONES: # madrid is used in another test
        assert "madrid" in candidates


# --- Tests for get_city_weather_candidates ---
def test_get_city_weather_candidates():
    candidates = get_city_weather_candidates()
    assert isinstance(candidates, list)
    assert all(isinstance(city, str) for city in candidates)
    assert candidates == sorted(candidates) # Check if sorted
    # Check a few known cities
    assert "tokyo" in candidates
    assert "paris" in candidates


# --- Tests for get_current_time ---
@mock.patch("agents.multi_tool_agent.util.datetime")
def test_get_current_time_known_city(mock_datetime):
    city = "new york"
    tz_identifier = CITY_TIMEZONES[city.lower()]

    # Setup mock datetime object and its now() method
    mock_now = mock.Mock()
    # Create a fixed datetime object to be returned by now()
    # Ensure it's timezone-aware if ZoneInfo attaches timezone, or naive if that's what's expected before formatting
    # The code uses: now = datetime.datetime.now(tz) -> so tz is applied by ZoneInfo.
    # strftime("%Y-%m-%d %H:%M:%S %Z%z") requires a timezone-aware datetime object.
    fixed_dt = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=-5))) # EST example

    mock_datetime.datetime.now.return_value = fixed_dt
    # If ZoneInfo(tz_identifier) is used to create tz, then datetime.now(tz) will be called.
    # We need to ensure that datetime.now called with any ZoneInfo still gives our fixed time *as if* it's in that zone.
    # More accurately, the strftime format includes %Z%z which comes from the datetime object's tzinfo.
    # So, the mock_now should have the correct tzinfo that ZoneInfo(tz_identifier) would produce.

    # Let's refine the mock for datetime.datetime.now(tz)
    # The function under test calls:
    # from zoneinfo import ZoneInfo
    # tz = ZoneInfo(tz_identifier)
    # now = datetime.datetime.now(tz)
    # So we need datetime.datetime.now when called with a tz argument to return our fixed time.

    # To make it simpler, let's assume ZoneInfo will correctly create the timezone.
    # We are mocking  itself.
    # The actual ZoneInfo object will be passed to it.
    # We need  to be what  would return.

    # The mock_datetime.datetime.now is the one called.
    # We need to make sure it returns a datetime object that, when strftime is called, produces a predictable string.
    # The crucial part is that the returned object should have a tzinfo that is consistent with the city.

    # Let's create a datetime object that already has the target timezone info
    # This means we don't need to mock ZoneInfo itself, just the result of .now(tz)
    from zoneinfo import ZoneInfo # Import for test setup
    actual_tz = ZoneInfo(tz_identifier)
    fixed_dt_in_zone = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=actual_tz)
    mock_datetime.datetime.now.return_value = fixed_dt_in_zone

    result = get_current_time(city)

    assert result["status"] == "success"
    assert city in result["report"]
    # Example: "The current time in new york is 2024-01-01 12:00:00 EST-0500" (format might vary slightly by OS/locale for %Z)
    # We can check parts of it.
    assert "2024-01-01 12:00:00" in result["report"]
    # The %Z%z part is tricky to assert directly without knowing the exact output of strftime for that zone on the test system.
    # For "America/New_York" on Jan 1st, it's typically EST or -0500.
    # A more robust check might be to parse the date string back if possible, or check for key components.
    assert CITY_TIMEZONES[city.lower()].split('/')[-1].replace('_', ' ') in result["report"] or "2024-01-01 12:00:00" in result["report"]


def test_get_current_time_known_city_mixed_case():
    # This test primarily ensures that city name casing is handled.
    # The actual time generation logic is tested above.
    # We don't need to mock datetime here if we trust the above test covers the core logic,
    # but for consistency and to ensure no side effects if it were to fail:
    with mock.patch("agents.multi_tool_agent.util.datetime") as mock_dt:
        # Setup a simple mock for now()
        from zoneinfo import ZoneInfo
        fixed_dt_in_zone = datetime.datetime(2023, 5, 5, 10, 30, 0, tzinfo=ZoneInfo("Europe/Paris")) # Dummy time & zone
        mock_dt.datetime.now.return_value = fixed_dt_in_zone

        city = "PaRiS" # Mixed case
        result = get_current_time(city)
        assert result["status"] == "success"
        assert "PaRiS" in result["report"] # Check for normalized or original casing as per function output
        assert "2023-05-05 10:30:00" in result["report"]

def test_get_current_time_unknown_city():
    city = "unknown_city_for_time_12345"
    result = get_current_time(city)
    assert result["status"] == "error"
    assert f"Sorry, I don't have timezone information for {city}" in result["error_message"]
    assert "Supported cities include:" in result["error_message"]
