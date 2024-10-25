from trip.routes import get_routes
from trip.hotels import get_hotels_by_location
from trip.restaurants import get_restaurants_by_location
from trip.weather import get_weather_forecast
from trip.others import get_places
from core.langchain_prompts import TripPlanPrompt


def extract(text, tag):
    """Extract text between two tags."""
    starting = "<" + tag + ">"
    ending = "</" + tag + ">"
    return text.split(starting)[1].split(ending)[0]


def plan_trip(
    origin, destination, start_date, end_date, dest_lat, dest_lng, budget_type="medium"
):
    routes = get_routes(origin, destination)
    print("routes generated")
    hotels = get_hotels_by_location(destination)
    print("hotels generated")
    restaurants = get_restaurants_by_location(destination)
    print("restaurants generated")
    weather = get_weather_forecast(dest_lat, dest_lng)
    print("weather generated")
    tourist_attraction = get_places(dest_lat, dest_lng, "tourist_attraction")
    print("tourist_attraction generated")
    

    plan = TripPlanPrompt.invoke(
        {
            "budget": budget_type,
            "origin": origin,
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "dest_lat": dest_lat,
            "dest_lng": dest_lng,
            "routes": routes,
            "hotels": hotels,
            "restaurants": restaurants,
            "weather": weather,
            "tourist_attraction": tourist_attraction,
        }
    ).content

    _title = extract(plan, "title")
    _summary = extract(plan, "summary")
    _routes = extract(plan, "routes")
    _hotels = extract(plan, "hotels")
    _restaurants = extract(plan, "restaurants")
    _weather = extract(plan, "weather")
    _cost = extract(plan, "cost")
    _itinerary = extract(plan, "itinerary")
    _tourist_attraction = extract(plan, "tourist_attractions")
    _map = extract(plan, "map")

    markdown = f"""
{_title}
{_summary}
{_routes}
{_hotels}
{_restaurants}
{_weather}
{_cost}
{_itinerary}
{_tourist_attraction}
    """

    return {
        "title": _title,
        "map": _map,
        "markdown": markdown,
    }


# x = plan_trip(
#     "uttara dhaka",
#     "CUET, Chittagong",
#     "25-10-2024",
#     "30-10-2024",
#     "22.3752",
#     "91.8349",
# )
