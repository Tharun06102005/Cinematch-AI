"""
CineMatch-AI Weather Module
----------------------------
Fetches real-time weather data from OpenWeather API and maps
weather conditions to movie genre suggestions.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -------------------- Configuration --------------------
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
IP_API_URL = "http://ip-api.com/json/"

# Timeout for HTTP requests (seconds)
REQUEST_TIMEOUT = 10

# -------------------- Weather-to-Genre Mapping --------------------
WEATHER_GENRE_MAP = {
    # Rainy / Stormy weather
    "thunderstorm": ["Drama", "Thriller"],
    "drizzle": ["Drama", "Thriller"],
    "rain": ["Drama", "Thriller"],

    # Clear / Sunny weather
    "clear": ["Adventure", "Comedy"],

    # Cloudy weather
    "clouds": ["Mystery", "Documentary"],

    # Snowy weather
    "snow": ["Romance", "Family"],

    # Misty / Foggy weather
    "mist": ["Horror", "Mystery"],
    "fog": ["Horror", "Mystery"],
    "haze": ["Horror", "Mystery"],
    "smoke": ["Horror", "Mystery"],
    "dust": ["Horror", "Mystery"],
    "sand": ["Horror", "Mystery"],
    "ash": ["Horror", "Mystery"],
    "squall": ["Drama", "Thriller"],
    "tornado": ["Drama", "Thriller"],

    # Additional friendly names for common conditions
    "sunny": ["Adventure", "Comedy"],
    "partly cloudy": ["Mystery", "Documentary"],
    "overcast": ["Mystery", "Documentary"],
    "light rain": ["Drama", "Thriller"],
    "heavy rain": ["Drama", "Thriller"],
    "freezing rain": ["Drama", "Thriller"],
    "heavy snow": ["Romance", "Family"],
    "sleet": ["Drama", "Thriller"],
    "blizzard": ["Romance", "Family"],
}

# -------------------- Genre Lookup Function --------------------
def get_genre_from_weather(weather_condition):
    """
    Map a weather condition string to a list of suggested movie genres.

    Parameters
    ----------
    weather_condition : str
        Description of the weather condition (e.g., 'Clear', 'Rain', 'Clouds').

    Returns
    -------
    list[str]
        Recommended genres for this weather condition.
    """
    try:
        if not weather_condition:
            return ["Comedy", "Adventure"]

        condition_lower = weather_condition.strip().lower()

        # Direct lookup first
        if condition_lower in WEATHER_GENRE_MAP:
            return WEATHER_GENRE_MAP[condition_lower]

        # Partial matching: check if any key is a substring of the condition
        # e.g., "light rain" contains "rain"
        for key, genres in WEATHER_GENRE_MAP.items():
            if key in condition_lower or condition_lower in key:
                return genres

        # Check OpenWeather main categories (the first word often matters)
        main_condition = condition_lower.split()[0] if condition_lower else ""
        if main_condition in WEATHER_GENRE_MAP:
            return WEATHER_GENRE_MAP[main_condition]

        # No match found
        print(f"[INFO] No genre mapping for weather condition: '{weather_condition}'. Using defaults.")
        return ["Comedy", "Adventure"]

    except Exception as e:
        print(f"[ERROR] get_genre_from_weather failed: {e}")
        return ["Comedy", "Adventure"]


# -------------------- City Auto-Detection --------------------
def _detect_city():
    """
    Auto-detect the user's city using the free ip-api.com service.

    Returns
    -------
    str or None
        City name if detected, None otherwise.
    """
    try:
        response = requests.get(IP_API_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            city = data.get("city")
            if city:
                print(f"[INFO] Auto-detected city: {city}")
                return city
            else:
                print("[WARN] ip-api.com returned no city name.")
                return None
        else:
            print(f"[WARN] ip-api.com lookup failed: {data.get('message', 'Unknown error')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"[WARN] Failed to auto-detect city (network error): {e}")
        return None
    except Exception as e:
        print(f"[WARN] Failed to auto-detect city: {e}")
        return None


# -------------------- Main Weather Function --------------------
def get_weather(city=None):
    """
    Fetch current weather for a given city (or auto-detect) and return
    weather info along with suggested movie genres.

    Parameters
    ----------
    city : str or None
        City name to fetch weather for. If None, auto-detect via ip-api.com.

    Returns
    -------
    dict
        Weather data with keys: city, temperature, weather_condition, genre_suggestion.
        If an error occurs, returns default values.
    """
    try:
        # 1. Determine the city
        if city is None or city.strip() == "":
            detected = _detect_city()
            if detected is None:
                print("[WARN] Could not auto-detect city. Using default fallback.")
                return _get_default_weather()
            city = detected
        else:
            city = city.strip()

        # 2. Validate API key
        if not OPENWEATHER_API_KEY:
            print("[ERROR] OPENWEATHER_API_KEY is not set in .env file.")
            return _get_default_weather(city=city)

        # 3. Fetch weather from OpenWeather API
        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
        }
        response = requests.get(OPENWEATHER_BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        # 4. Extract relevant weather data
        weather_main = data.get("weather", [{}])[0].get("main", "Clear")
        weather_description = data.get("weather", [{}])[0].get("description", "clear sky")
        temperature = data.get("main", {}).get("temp", 25.0)
        city_name = data.get("name", city)

        # 5. Map to genres
        genre_suggestion = get_genre_from_weather(weather_description)
        # Also try with main category as backup for more specific matches
        if not genre_suggestion or genre_suggestion == ["Comedy", "Adventure"]:
            genre_suggestion = get_genre_from_weather(weather_main)

        # 6. Build and return result
        result = {
            "city": city_name,
            "temperature": round(temperature, 1),
            "weather_condition": weather_description,
            "genre_suggestion": genre_suggestion,
        }

        print(
            f"[INFO] Weather in {city_name}: {temperature}°C, "
            f"{weather_description} → Genres: {', '.join(genre_suggestion)}"
        )
        return result

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, "response") and e.response is not None else "?"
        print(f"[ERROR] OpenWeather API returned HTTP {status_code}: {e}")
        return _get_default_weather(city=city or "Unknown")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Network connection failed when contacting OpenWeather API.")
        return _get_default_weather(city=city or "Unknown")
    except requests.exceptions.Timeout:
        print("[ERROR] OpenWeather API request timed out.")
        return _get_default_weather(city=city or "Unknown")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] OpenWeather API request failed: {e}")
        return _get_default_weather(city=city or "Unknown")
    except KeyError as e:
        print(f"[ERROR] Unexpected OpenWeather API response format (missing key: {e})")
        return _get_default_weather(city=city or "Unknown")
    except Exception as e:
        print(f"[ERROR] get_weather failed: {e}")
        return _get_default_weather(city=city or "Unknown")


# -------------------- Default Fallback --------------------
def _get_default_weather(city="Unknown"):
    """
    Return default weather data when the API call fails.

    Parameters
    ----------
    city : str
        City name to include in the response.

    Returns
    -------
    dict
        Default weather data with Clear condition and Comedy/Adventure genres.
    """
    return {
        "city": city,
        "temperature": 25.0,
        "weather_condition": "Clear",
        "genre_suggestion": ["Comedy", "Adventure"],
    }


# -------------------- Initialization --------------------
if __name__ == "__main__":
    # When run directly, test with auto-detection
    print("Testing weather module with auto-detected city...")
    result = get_weather()
    print(f"Result: {result}")

print("Weather module loaded successfully")
