import datetime
from copy import deepcopy
from zoneinfo import ZoneInfo

from typing import Dict, List


# Mapping of city names to their respective time zones
CITY_TIMEZONES: Dict[str, str] = {
    "new york": "America/New_York",
    "tokyo": "Asia/Tokyo",
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "los angeles": "America/Los_Angeles",
    "chicago": "America/Chicago",
    "sydney": "Australia/Sydney",
    "hong kong": "Asia/Hong_Kong",
    "singapore": "Asia/Singapore",
    "dubai": "Asia/Dubai",
    "moscow": "Europe/Moscow",
    "berlin": "Europe/Berlin",
    "madrid": "Europe/Madrid",
    "rome": "Europe/Rome",
    "beijing": "Asia/Shanghai",
    "seoul": "Asia/Seoul",
    "mumbai": "Asia/Kolkata",
    "sao paulo": "America/Sao_Paulo",
    "mexico city": "America/Mexico_City",
    "toronto": "America/Toronto",
    "vancouver": "America/Vancouver",
    "cairo": "Africa/Cairo",
    "johannesburg": "Africa/Johannesburg",
    "lagos": "Africa/Lagos",
    "bangkok": "Asia/Bangkok",
    "manila": "Asia/Manila",
    "jakarta": "Asia/Jakarta",
    "kuala lumpur": "Asia/Kuala_Lumpur",
    "istanbul": "Europe/Istanbul",
    "stockholm": "Europe/Stockholm",
    "oslo": "Europe/Oslo",
    "helsinki": "Europe/Helsinki",
    "vienna": "Europe/Vienna",
    "zurich": "Europe/Zurich",
    "amsterdam": "Europe/Amsterdam",
    "brussels": "Europe/Brussels",
    "copenhagen": "Europe/Copenhagen",
    "prague": "Europe/Prague",
    "warsaw": "Europe/Warsaw",
    "budapest": "Europe/Budapest",
    "athens": "Europe/Athens",
    "lisbon": "Europe/Lisbon",
}


def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_city_timezones_candidates() -> List[str]:
    """Returns a list of city names for which time zone information is available.

    Returns:
        List[str]: A list of city names.
    """
    return sorted(CITY_TIMEZONES.keys())


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """
    
    # 都市名とタイムゾーンのマッピング
    city_timezones = deepcopy(CITY_TIMEZONES)
    
    city_lower = city.lower()
    if city_lower in city_timezones:
        tz_identifier = city_timezones[city_lower]
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}. "
                f"Supported cities include: {', '.join(sorted(city_timezones.keys()))}"
            ),
        }

    try:
        tz = ZoneInfo(tz_identifier)
        now = datetime.datetime.now(tz)
        report = f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
        return {"status": "success", "report": report}
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error getting time for {city}: {str(e)}"
        }


if __name__ == "__main__":
    pass
