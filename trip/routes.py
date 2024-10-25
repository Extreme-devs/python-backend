from core.config import settings
import googlemaps
from datetime import datetime
import json
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
from enum import Enum


class TransitMode(Enum):
    TRANSIT = "transit"  # Bus and Train
    DRIVING = "driving"  # Car and Motorcycle
    BICYCLING = "bicycling"
    WALKING = "walking"


@dataclass
class RouteOption:
    mode: TransitMode
    duration: str
    distance: str
    steps: List[Dict]
    fare: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None


class TransitRouter:
    def __init__(self, api_key: str):
        """Initialize the Google Maps client with API key."""
        try:
            self.gmaps = googlemaps.Client(key=api_key)
            # Verify API key
            self.gmaps.geocode("New York")
        except Exception as e:
            raise ValueError(f"Failed to initialize Google Maps client: {str(e)}")

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_all_routes(
        self, origin: str, destination: str, departure_time: Optional[datetime] = None
    ) -> Dict[TransitMode, List[RouteOption]]:
        """
        Get available routes for all transportation modes.

        Args:
            origin: Starting location
            destination: Ending location
            departure_time: Optional departure time (defaults to now)

        Returns:
            Dictionary of transit modes and their route options
        """
        if departure_time is None:
            departure_time = datetime.now()

        routes = {}

        for mode in TransitMode:
            try:
                if mode == TransitMode.TRANSIT:
                    # For transit, get multiple alternatives
                    routes[mode] = self._get_transit_routes(
                        origin, destination, departure_time
                    )
                else:
                    # For other modes, get primary route
                    route = self._get_route(
                        origin, destination, mode.value, departure_time
                    )
                    if route:
                        routes[mode] = [route]
            except Exception as e:
                self.logger.error(f"Error getting {mode.value} routes: {str(e)}")
                continue

        return routes

    def _get_transit_routes(
        self, origin: str, destination: str, departure_time: datetime
    ) -> List[RouteOption]:
        """Get available public transit routes (bus and train)."""
        try:
            directions = self.gmaps.directions(
                origin=origin,
                destination=destination,
                mode=TransitMode.TRANSIT.value,
                alternatives=True,
                departure_time=departure_time,
            )

            routes = []
            for route in directions:
                leg = route["legs"][0]  # Get the first (and only) leg

                # Extract transit-specific details
                steps = []
                for step in leg["steps"]:
                    step_info = {
                        "instruction": step["html_instructions"],
                        "distance": step["distance"]["text"],
                        "duration": step["duration"]["text"],
                    }

                    # Add transit details if available
                    if step.get("transit_details"):
                        transit = step["transit_details"]
                        step_info.update(
                            {
                                "type": "transit",
                                "line": transit["line"].get(
                                    "short_name", transit["line"].get("name")
                                ),
                                "vehicle": transit["line"]["vehicle"]["type"],
                                "departure_stop": transit["departure_stop"]["name"],
                                "arrival_stop": transit["arrival_stop"]["name"],
                                "departure_time": transit["departure_time"]["text"],
                                "arrival_time": transit["arrival_time"]["text"],
                                "num_stops": transit.get("num_stops", 0),
                            }
                        )

                    steps.append(step_info)

                # Create RouteOption
                route_option = RouteOption(
                    mode=TransitMode.TRANSIT,
                    duration=leg["duration"]["text"],
                    distance=leg["distance"]["text"],
                    steps=steps,
                    departure_time=leg["departure_time"]["text"],
                    arrival_time=leg["arrival_time"]["text"],
                    fare=leg.get("fare", {}).get("text") if "fare" in leg else None,
                )
                routes.append(route_option)

            return routes

        except Exception as e:
            self.logger.error(f"Error getting transit routes: {str(e)}")
            return []

    def _get_route(
        self, origin: str, destination: str, mode: str, departure_time: datetime
    ) -> Optional[RouteOption]:
        """Get route for a specific transportation mode."""
        try:
            directions = self.gmaps.directions(
                origin=origin,
                destination=destination,
                mode=mode,
                departure_time=departure_time,
            )

            if not directions:
                return None

            route = directions[0]
            leg = route["legs"][0]

            # Process steps
            steps = []
            for step in leg["steps"]:
                step_info = {
                    "instruction": step["html_instructions"],
                    "distance": step["distance"]["text"],
                    "duration": step["duration"]["text"],
                }
                steps.append(step_info)

            return RouteOption(
                mode=TransitMode(mode),
                duration=leg["duration"]["text"],
                distance=leg["distance"]["text"],
                steps=steps,
            )

        except Exception as e:
            self.logger.error(f"Error getting {mode} route: {str(e)}")
            return None


def get_routes(origin: str, destination: str):
    """Example usage of the TransitRouter."""
    api_key = settings.GOOGLEMAPS_API_KEY
    response = ""
    try:
        router = TransitRouter(api_key)
        routes = router.get_all_routes(origin, destination)
        response += f"\nRoutes from {origin} to {destination}:"
        response += "=" * 50
        for mode, route_options in routes.items():
            response += f"\n{mode.value.upper()} OPTIONS:"
            for i, route in enumerate(route_options, 1):
                response += f"\nOption {i}:"
                response += f"Duration: {route.duration}"
                response += f"Distance: {route.distance}"
                if route.fare:
                    response += f"Fare: {route.fare}"
                if route.departure_time:
                    response += f"Departure: {route.departure_time}"
                if route.arrival_time:
                    response += f"Arrival: {route.arrival_time}"
                response += "\nDirections:"
                for j, step in enumerate(route.steps, 1):
                    response += f"{j}. {step['instruction']} ({step['distance']})"
                    if "type" in step and step["type"] == "transit":
                        response += f"   → {step['line']} {step['vehicle']}"
                        response += f"   → From: {step['departure_stop']} at {step['departure_time']}"
                        response += (
                            f"   → To: {step['arrival_stop']} at {step['arrival_time']}"
                        )
                response += "-" * 30

    except Exception as e:
        response += f"An error occurred: {str(e)}"
    return response
