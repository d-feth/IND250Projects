import requests
from requests.exceptions import Timeout, ConnectionError, RequestException

# ----------------------------------------
# API endpoints and request timeout setting
# ----------------------------------------
# These are the URLs we use to talk to Open-Meteo.
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# If the API takes longer than this many seconds, the request will fail.
TIMEOUT_SECONDS = 10


# ----------------------------------------
# State name lookup tables
# ----------------------------------------
# This dictionary lets us recognize full state names.
US_STATES = {
    "alabama": "Alabama",
    "alaska": "Alaska",
    "arizona": "Arizona",
    "arkansas": "Arkansas",
    "california": "California",
    "colorado": "Colorado",
    "connecticut": "Connecticut",
    "delaware": "Delaware",
    "florida": "Florida",
    "georgia": "Georgia",
    "hawaii": "Hawaii",
    "idaho": "Idaho",
    "illinois": "Illinois",
    "indiana": "Indiana",
    "iowa": "Iowa",
    "kansas": "Kansas",
    "kentucky": "Kentucky",
    "louisiana": "Louisiana",
    "maine": "Maine",
    "maryland": "Maryland",
    "massachusetts": "Massachusetts",
    "michigan": "Michigan",
    "minnesota": "Minnesota",
    "mississippi": "Mississippi",
    "missouri": "Missouri",
    "montana": "Montana",
    "nebraska": "Nebraska",
    "nevada": "Nevada",
    "new hampshire": "New Hampshire",
    "new jersey": "New Jersey",
    "new mexico": "New Mexico",
    "new york": "New York",
    "north carolina": "North Carolina",
    "north dakota": "North Dakota",
    "ohio": "Ohio",
    "oklahoma": "Oklahoma",
    "oregon": "Oregon",
    "pennsylvania": "Pennsylvania",
    "rhode island": "Rhode Island",
    "south carolina": "South Carolina",
    "south dakota": "South Dakota",
    "tennessee": "Tennessee",
    "texas": "Texas",
    "utah": "Utah",
    "vermont": "Vermont",
    "virginia": "Virginia",
    "washington": "Washington",
    "west virginia": "West Virginia",
    "wisconsin": "Wisconsin",
    "wyoming": "Wyoming",
    "district of columbia": "District of Columbia",
}

# This one is optional bonus support for abbreviations like VA or NY.
STATE_ABBREVIATIONS = {
    "al": "Alabama",
    "ak": "Alaska",
    "az": "Arizona",
    "ar": "Arkansas",
    "ca": "California",
    "co": "Colorado",
    "ct": "Connecticut",
    "de": "Delaware",
    "fl": "Florida",
    "ga": "Georgia",
    "hi": "Hawaii",
    "id": "Idaho",
    "il": "Illinois",
    "in": "Indiana",
    "ia": "Iowa",
    "ks": "Kansas",
    "ky": "Kentucky",
    "la": "Louisiana",
    "me": "Maine",
    "md": "Maryland",
    "ma": "Massachusetts",
    "mi": "Michigan",
    "mn": "Minnesota",
    "ms": "Mississippi",
    "mo": "Missouri",
    "mt": "Montana",
    "ne": "Nebraska",
    "nv": "Nevada",
    "nh": "New Hampshire",
    "nj": "New Jersey",
    "nm": "New Mexico",
    "ny": "New York",
    "nc": "North Carolina",
    "nd": "North Dakota",
    "oh": "Ohio",
    "ok": "Oklahoma",
    "or": "Oregon",
    "pa": "Pennsylvania",
    "ri": "Rhode Island",
    "sc": "South Carolina",
    "sd": "South Dakota",
    "tn": "Tennessee",
    "tx": "Texas",
    "ut": "Utah",
    "vt": "Vermont",
    "va": "Virginia",
    "wa": "Washington",
    "wv": "West Virginia",
    "wi": "Wisconsin",
    "wy": "Wyoming",
    "dc": "District of Columbia",
}


# ----------------------------------------
# Helper function: clean up extra spaces
# ----------------------------------------
def normalize_whitespace(text: str) -> str:
    """
    Removes extra spaces from a string.

    Example:
    "  New    York  " -> "New York"
    """
    return " ".join(text.strip().split())


# ----------------------------------------
# Helper function: validate/standardize state
# ----------------------------------------
def normalize_state_input(state_input: str) -> str | None:
    """
    Converts the user's state input into a properly formatted full state name.

    Returns:
        Full state name as a string if valid
        None if the state is not recognized
    """
    state_key = normalize_whitespace(state_input).lower()

    if state_key in US_STATES:
        return US_STATES[state_key]

    if state_key in STATE_ABBREVIATIONS:
        return STATE_ABBREVIATIONS[state_key]

    return None


# ----------------------------------------
# Get location info from Open-Meteo geocoding
# ----------------------------------------
def get_location(city: str, state: str) -> dict | None:
    """
    Searches the Open-Meteo geocoding API for a matching U.S. city/state.

    Why do we need this?
    The forecast API needs latitude and longitude, not just city/state names.

    Returns:
        A result dictionary with location data if found
        None if no matching location exists
    """
    params = {
        "name": city,           # city name entered by the user
        "count": 20,            # ask for up to 20 possible matches
        "language": "en",       # return results in English
        "format": "json",       # request JSON response
        "countryCode": "US",    # only search within the United States
    }

    # Send GET request to geocoding API
    response = requests.get(GEOCODING_URL, params=params, timeout=TIMEOUT_SECONDS)

    # Raise an error if the API returned a bad status code
    response.raise_for_status()

    # Convert JSON response into a Python dictionary
    data = response.json()

    # Pull out the "results" list, or use an empty list if missing
    results = data.get("results", [])

    # If no results came back, location was not found
    if not results:
        return None

    # Normalize city and state so comparison is more reliable
    target_city = normalize_whitespace(city).lower()
    target_state = normalize_whitespace(state).lower()

    # First try to find an exact match for both city and state
    for result in results:
        result_city = normalize_whitespace(result.get("name", "")).lower()
        result_state = normalize_whitespace(result.get("admin1", "")).lower()

        if result_city == target_city and result_state == target_state:
            return result

    # If exact city+state wasn't found, try just matching the state
    # This is a fallback in case the city format differs slightly.
    for result in results:
        result_state = normalize_whitespace(result.get("admin1", "")).lower()

        if result_state == target_state:
            return result

    # No matching state found
    return None


# ----------------------------------------
# Get 10-day forecast using latitude/longitude
# ----------------------------------------
def get_forecast(latitude: float, longitude: float) -> dict:
    """
    Calls the Open-Meteo forecast API using latitude and longitude.

    Returns:
        Forecast data as a Python dictionary
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
        "timezone": "auto",
        "forecast_days": 10,
    }

    # Send GET request to forecast API
    response = requests.get(FORECAST_URL, params=params, timeout=TIMEOUT_SECONDS)

    # Raise an error if the request failed
    response.raise_for_status()

    # Convert JSON to Python dictionary and return it
    return response.json()


# ----------------------------------------
# Print forecast in table form
# ----------------------------------------
def print_forecast(city_name: str, state_name: str, forecast_data: dict) -> None:
    """
    Extracts daily forecast data and prints it in a neat table.
    """
    # Get the "daily" section from the API response
    daily = forecast_data.get("daily", {})

    # Pull out the lists we need
    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    rain = daily.get("precipitation_sum", [])

    # Print title/header
    print(f"\n--- 10-Day Forecast for {city_name}, {state_name} ---")
    print(f"{'Date':<12} | {'Max Temp':>9} | {'Min Temp':>9} | {'Rain':>10}")
    print("-" * 54)

    # zip() lets us loop through all four lists at once
    for date, max_temp, min_temp, precip in zip(dates, max_temps, min_temps, rain):
        print(f"{date:<12} | {max_temp:>8.1f}°F | {min_temp:>8.1f}°F | {precip:>7.3f}inch")


# ----------------------------------------
# Main program logic
# ----------------------------------------
def main() -> None:
    """
    Runs the overall program:
    1. Ask user for city and state
    2. Validate input
    3. Find location coordinates
    4. Get forecast
    5. Print results
    6. Handle errors if something goes wrong
    """
    print("10-Day Weather Forecast")

    # Ask user for input
    city = input("Enter city: ").strip()
    state_input = input("Enter state: ").strip()

    # Make sure neither field is blank
    if not city or not state_input:
        print("Error: City and state are required.")
        return

    # Convert user state input into a standard full state name
    normalized_state = normalize_state_input(state_input)

    # If state isn't valid, stop the program
    if not normalized_state:
        print("Error: State not recognized. Please enter a full U.S. state name.")
        return

    try:
        # Step 1: Find the location
        location = get_location(city, normalized_state)

        # If no location matched, stop
        if location is None:
            print(f"Location not found for {city}, {normalized_state}.")
            return

        # Extract latitude and longitude from geocoding result
        latitude = location["latitude"]
        longitude = location["longitude"]

        # Use API-returned city/state names if available
        city_name = location.get("name", city)
        state_name = location.get("admin1", normalized_state)

        # Step 2: Get the forecast
        forecast = get_forecast(latitude, longitude)

        # Step 3: Print the results
        print_forecast(city_name, state_name, forecast)

    except Timeout:
        # Happens if the API takes too long to respond
        print("Error: The request timed out. Please try again later.")

    except ConnectionError:
        # Happens if internet is down or server can't be reached
        print("Error: Could not connect to the weather service. Check your internet connection.")

    except RequestException as e:
        # General request-related errors
        print(f"Error: Request failed: {e}")

    except KeyError as e:
        # Happens if expected data is missing from the API response
        print(f"Error: Unexpected response format. Missing field: {e}")

    except Exception as e:
        # Catch-all for any other unexpected issue
        print(f"An unexpected error occurred: {e}")


# ----------------------------------------
# Program entry point
# ----------------------------------------
# This makes sure main() only runs when this file is executed directly.
if __name__ == "__main__":
    main()
