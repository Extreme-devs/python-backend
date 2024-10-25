import requests
from core.config import settings

def get_weather_forecast(lat, lng):
    url = "https://ai-weather-by-meteosource.p.rapidapi.com/time_machine"
    querystring = {"lat": lat, "lon": lng, "date": "2021-08-24", "units": "auto"}

    headers = {
        "x-rapidapi-key": settings.WEATHER_API_KEY,
        "x-rapidapi-host": "ai-weather-by-meteosource.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers, params=querystring)
    return response.json()
