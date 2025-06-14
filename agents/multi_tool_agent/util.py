import datetime
from copy import deepcopy
from zoneinfo import ZoneInfo

from typing import Dict, List


# Mapping of city names to their weather data
CITY_WEATHER: Dict[str, Dict[str, any]] = {
    "new york": {
        "temperature_c": 25,
        "temperature_f": 77,
        "condition": "sunny",
        "humidity": 65,
        "wind_speed": "10 km/h"
    },
    "tokyo": {
        "temperature_c": 22,
        "temperature_f": 72,
        "condition": "partly cloudy",
        "humidity": 70,
        "wind_speed": "8 km/h"
    },
    "london": {
        "temperature_c": 18,
        "temperature_f": 64,
        "condition": "rainy",
        "humidity": 85,
        "wind_speed": "15 km/h"
    },
    "paris": {
        "temperature_c": 20,
        "temperature_f": 68,
        "condition": "cloudy",
        "humidity": 75,
        "wind_speed": "12 km/h"
    },
    "los angeles": {
        "temperature_c": 28,
        "temperature_f": 82,
        "condition": "sunny",
        "humidity": 55,
        "wind_speed": "5 km/h"
    },
    "chicago": {
        "temperature_c": 23,
        "temperature_f": 73,
        "condition": "windy",
        "humidity": 60,
        "wind_speed": "20 km/h"
    },
    "sydney": {
        "temperature_c": 24,
        "temperature_f": 75,
        "condition": "sunny",
        "humidity": 60,
        "wind_speed": "18 km/h"
    },
    "hong kong": {
        "temperature_c": 29,
        "temperature_f": 84,
        "condition": "humid and cloudy",
        "humidity": 88,
        "wind_speed": "12 km/h"
    },
    "singapore": {
        "temperature_c": 30,
        "temperature_f": 86,
        "condition": "humid and sunny",
        "humidity": 90,
        "wind_speed": "7 km/h"
    },
    "dubai": {
        "temperature_c": 35,
        "temperature_f": 95,
        "condition": "hot and sunny",
        "humidity": 40,
        "wind_speed": "8 km/h"
    },
    "moscow": {
        "temperature_c": 15,
        "temperature_f": 59,
        "condition": "cold and cloudy",
        "humidity": 70,
        "wind_speed": "14 km/h"
    },
    "berlin": {
        "temperature_c": 19,
        "temperature_f": 66,
        "condition": "overcast",
        "humidity": 72,
        "wind_speed": "11 km/h"
    },
    "beijing": {
        "temperature_c": 26,
        "temperature_f": 79,
        "condition": "hazy",
        "humidity": 65,
        "wind_speed": "9 km/h"
    },
    "mumbai": {
        "temperature_c": 32,
        "temperature_f": 90,
        "condition": "hot and humid",
        "humidity": 85,
        "wind_speed": "13 km/h"
    },
    "sao paulo": {
        "temperature_c": 21,
        "temperature_f": 70,
        "condition": "mild and partly cloudy",
        "humidity": 68,
        "wind_speed": "6 km/h"
    }
}

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
    city_lower = city.lower()
    if city_lower in CITY_WEATHER:
        data = CITY_WEATHER[city_lower]
        return {
            "status": "success",
            "report": (
                f"The weather in {city} is {data['condition']} with a temperature of "
                f"{data['temperature_c']} degrees Celsius ({data['temperature_f']} degrees Fahrenheit). "
                f"Humidity: {data['humidity']}%, Wind speed: {data['wind_speed']}"
            ),
        }
    else:
        # For cities not in the weather data but in timezone list, provide a generic response
        if city_lower in CITY_TIMEZONES:
            return {
                "status": "success",
                "report": f"Weather information for {city} is currently unavailable, but the city is supported.",
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


def get_city_weather_candidates() -> List[str]:
    """Returns a list of city names for which weather information is available.

    Returns:
        List[str]: A list of city names.
    """
    return sorted(CITY_WEATHER.keys())


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
