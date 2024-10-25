import requests
from core.config import settings


def get_coordinates(location):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": location, "key": settings.GOOGLEMAPS_API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            location_data = data["results"][0]["geometry"]["location"]
            return location_data["lat"], location_data["lng"]
        else:
            return "Location not found"
    else:
        return f"Error: {response.status_code}"


# location = input()
# lat, lng = get_coordinates(settings.GOOGLEMAPS_API_KEY, location)
# print(f"Coordinates of {location}: Latitude = {lat}, Longitude = {lng}")
