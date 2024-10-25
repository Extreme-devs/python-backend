from core.config import settings
import requests
from math import radians, cos, sin, sqrt, atan2

# Define available place types according to Google Places API
PLACE_TYPES = [
    "accounting",
    "airport",
    "amusement_park",
    "aquarium",
    "art_gallery",
    "atm",
    "bakery",
    "bank",
    "bar",
    "beauty_salon",
    "bicycle_store",
    "book_store",
    "bowling_alley",
    "bus_station",
    "cafe",
    "campground",
    "car_dealer",
    "car_rental",
    "car_repair",
    "car_wash",
    "casino",
    "cemetery",
    "church",
    "cinema",
    "city_hall",
    "clothing_store",
    "convenience_store",
    "courthouse",
    "dentist",
    "department_store",
    "doctor",
    "drugstore",
    "electrician",
    "electronics_store",
    "embassy",
    "fire_station",
    "florist",
    "funeral_home",
    "furniture_store",
    "gas_station",
    "gym",
    "hair_care",
    "hardware_store",
    "hindu_temple",
    "hospital",
    "jewelry_store",
    "laundry",
    "lawyer",
    "library",
    "light_rail_station",
    "liquor_store",
    "local_government_office",
    "locksmith",
    "lodging",
    "mosque",
    "movie_rental",
    "museum",
    "night_club",
    "park",
    "parking",
    "pet_store",
    "pharmacy",
    "physiotherapist",
    "police",
    "post_office",
    "real_estate_agency",
    "restaurant",
    "school",
    "shoe_store",
    "shopping_mall",
    "spa",
    "stadium",
    "subway_station",
    "supermarket",
    "synagogue",
    "taxi_stand",
    "train_station",
    "transit_station",
    "travel_agency",
    "university",
    "veterinary_care",
    "zoo",
]


class PlaceFinder:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    def get_available_types(self):
        """Return the list of all available place types"""
        return PLACE_TYPES

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        R = 6371.0  # Radius of the Earth in km
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = (
            sin(dlat / 2) ** 2
            + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        )
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c  # in kilometers
        return distance * 1000  # Convert to meters

    def find_places(self, user_latitude, user_longitude, place_type, radius=1500):
        """
        Find places of specified type within given radius

        Parameters:
        user_latitude (float): User's latitude
        user_longitude (float): User's longitude
        place_type (str): Type of place to search for
        radius (int): Search radius in meters (default: 1500)
        """
        # if place_type not in PLACE_TYPES:
        #     raise ValueError(
        #         f"Invalid place type. Please use get_available_types() to see valid options."
        #     )

        params = {
            "location": f"{user_latitude},{user_longitude}",
            "radius": radius,
            "type": place_type,
            "key": self.api_key,
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise exception for bad status codes
            data = response.json()

            if data.get("status") != "OK" and data.get("status") != "ZERO_RESULTS":
                raise Exception(
                    f"API Error: {data.get('status')} - {data.get('error_message', 'Unknown error')}"
                )

            results = []
            if data.get("results"):
                for place in data["results"]:
                    place_info = {
                        "name": place.get("name"),
                        "address": place.get("vicinity"),
                        "latitude": place["geometry"]["location"]["lat"],
                        "longitude": place["geometry"]["location"]["lng"],
                        "distance": self.calculate_distance(
                            user_latitude,
                            user_longitude,
                            place["geometry"]["location"]["lat"],
                            place["geometry"]["location"]["lng"],
                        ),
                        "rating": place.get("rating", "N/A"),
                        "total_ratings": place.get("user_ratings_total", "N/A"),
                    }

                    # Add photo URL if available
                    if place.get("photos"):
                        photo_reference = place["photos"][0]["photo_reference"]
                        place_info["photo_url"] = (
                            f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={self.api_key}"
                        )
                    else:
                        place_info["photo_url"] = "No image available"

                    results.append(place_info)

            return results

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")


def get_places(user_latitude, user_longitude, place_type):
    user_latitude = float(user_latitude)
    user_longitude = float(user_longitude)
    finder = PlaceFinder(settings.GOOGLEMAPS_API_KEY)
    response = ""
    try:
        places = finder.find_places(user_latitude, user_longitude, place_type)
        if places:
            response += f"\nFound {len(places)} places of type '{place_type}':"
            for place in places:
                response += "\n" + "=" * 40
                response += f"Name: {place['name']}"
                response += f"Address: {place['address']}"
                response += f"Distance: {place['distance']:.2f} meters"
                response += (
                    f"Rating: {place['rating']} ({place['total_ratings']} reviews)"
                )
                response += f"Image: {place['photo_url']}"
        else:
            response += "No places found."

    except Exception as e:
        response += f"Error: {str(e)}"
    return response
