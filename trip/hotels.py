import requests
import datetime
from rich import print
import json
from core.config import settings

today = datetime.datetime.now()
check_in_date = today + datetime.timedelta(days=7)
check_out_date = check_in_date + datetime.timedelta(days=1)
check_in_date_str = check_in_date.strftime("%Y-%m-%d")
check_out_date_str = check_out_date.strftime("%Y-%m-%d")


def get_hotel_locations(location):
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchLocation"
    querystring = {"query": location}
    headers = {
        "x-rapidapi-key": settings.TRIPADVISER_API_KEY,
        "x-rapidapi-host": "tripadvisor16.p.rapidapi.com",
    }
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()


def get_hotel_details(hotel_id):
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/getHotelDetails"
    querystring = {
        "id": hotel_id,
        "checkIn": check_in_date_str,
        "checkOut": check_out_date,
        "currency": "BDT",
    }

    headers = {
        "x-rapidapi-key": settings.TRIPADVISER_API_KEY,
        "x-rapidapi-host": "tripadvisor16.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

def get_hotels_by_location(location):
    geo_locations = get_hotel_locations(location)
    hotels = []
    for loc in geo_locations["data"]:
        geoId = loc["geoId"]
        querystring = {
            "geoId": geoId,
            "checkIn": check_in_date_str,
            "checkOut": check_out_date_str,
            "pageNumber": "1",
            "currencyCode": "BDT",
        }
        url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchHotels"
        headers = {
            "x-rapidapi-key": settings.TRIPADVISER_API_KEY,
            "x-rapidapi-host": "tripadvisor16.p.rapidapi.com",
        }
        response = requests.get(url, headers=headers, params=querystring)
        hotels += response.json()["data"]
        break
    return hotels[:5]


def get_hotels_by_coord(lat, lng):
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchHotelsByLocation"

    querystring = {
        "latitude": lat,
        "longitude": lng,
        "pageNumber": "1",
        "currencyCode": "BDT",
    }

    headers = {
        "x-rapidapi-key": settings.TRIPADVISER_API_KEY,
        "x-rapidapi-host": "tripadvisor16.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers, params=querystring)

    return response.json()