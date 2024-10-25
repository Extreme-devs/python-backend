from core.config import settings
import requests
import datetime
from rich import print
import json


def get_restaurant_locations(location):
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/restaurant/searchLocation"
    querystring = {"query": location}
    headers = {
        "x-rapidapi-key": settings.TRIPADVISER_API_KEY,
        "x-rapidapi-host": "tripadvisor16.p.rapidapi.com",
    }
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()


def get_restaurant_details(restaurant_id):
    url = (
        "https://tripadvisor16.p.rapidapi.com/api/v1/restaurant/getRestaurantDetailsV2"
    )

    querystring = {"restaurantsId": restaurant_id, "currencyCode": "BDT"}

    headers = {
        "x-rapidapi-key": settings.TRIPADVISER_API_KEY,
        "x-rapidapi-host": "tripadvisor16.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers, params=querystring)
    return response.json()


def get_restaurants_by_location(location):
    geo_locations = get_restaurant_locations(location)
    restaurants = []
    for loc in geo_locations["data"]:
        locationId = loc["locationId"]
        url = "https://tripadvisor16.p.rapidapi.com/api/v1/restaurant/searchRestaurants"
        querystring = {"locationId": locationId}
        headers = {
            "x-rapidapi-key": settings.TRIPADVISER_API_KEY,
            "x-rapidapi-host": "tripadvisor16.p.rapidapi.com",
        }
        response = requests.get(url, headers=headers, params=querystring)
        restaurants += response.json()["data"]["data"]
        break

    return restaurants[:5]
