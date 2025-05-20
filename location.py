port_coords = {
    "Baltic Sea": (58.0, 20.0),
    "West Mediterranean": (40.5, 4.5),
    "Central Mediterranean": (34.0, 17.0),
    "Adriatic Sea": (43.0, 15.5),
    "Great North Sea": (58.0, 2.0),
    "Celtic Sea": (54.0, -12.0),
    "Iberian Cost": (41.0, -11.0),
    "Aegian Sea": (38.0, 25.0),
    "Black Sea": (43, 33.0),
}

import numpy as np
import requests
from datetime import datetime, timedelta

def get_historical_weather_open_meteo(region):
    """
    Retrieves historical weather data (strongest wind and lowest temperature)
    for the last year for a given region using Open-Meteo archive API.

    Args:
        region (str): The name of the region (key in port_coords).

    Returns:
        dict or str: A dictionary with historical weather data (region, period,
                     strongest wind, lowest temperature) or an error message string.
    """
    if region not in port_coords:
        return f"Invalid Region: {region}"

    lat, lon = port_coords[region]

    # Calculate the dates for the last year
    end_date = datetime.now() - timedelta(days=1) # Up to yesterday
    start_date = end_date - timedelta(days=365)  # One year before yesterday

    # Format dates as YYYY-MM-DD strings
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Endpoint for historical data (archive)
    url = (
        f"https://archive-api.open-meteo.com/v1/era5"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_min,wind_speed_10m_max"
        f"&start_date={start_date_str}"
        f"&end_date={end_date_str}"
        f"&timezone=auto"
    )

    try:
        response = requests.get(url)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        return f"Error contacting API: {e}"

    data = response.json()

    # Check if 'daily' data is present and not empty
    if 'daily' not in data or not data['daily']:
         return f"No historical daily data found for region {region} in the specified period."

    # Find the minimum temperature and maximum wind speed over the year
    # Use .get() with a default value to handle missing keys gracefully
    daily_temps_min = data['daily'].get('temperature_2m_min', [])
    daily_winds_max = data['daily'].get('wind_speed_10m_max', [])

    # Handle cases where data lists might be empty even if 'daily' exists
    if not daily_temps_min or not daily_winds_max:
         return f"Could not find valid min temperature or max wind speed data for region {region}."

    # Calculate the average of the daily minimum temperatures and daily maximum wind speeds
    average_min_temp_C = np.mean(daily_temps_min)
    average_max_wind_speed_kmh = np.mean(daily_winds_max)


    return {
        "region": region,
        "period": f"{start_date_str} to {end_date_str}",
        "average_max_wind_kmh": round(average_max_wind_speed_kmh, 1),
        "average_min_temp_C": round(average_min_temp_C, 1)
    }

