from operator import itemgetter
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from .utils import image_to_base64
from .langchain_init import chatOpenAI


DefaultPrompt = PromptTemplate.from_template("{text}") | chatOpenAI

VlogGenerationPrompt = (
    PromptTemplate.from_template(
        """
You will provide me a json object that will be used to generate a video script. 
This video is based on a trip that I made recently. I will provide you my trip details and you will have to generate a video script for me. Make the video as interesting as possible. Also, keep the length of the video less than 30 seconds. Try to use all the resources I provide you about my trip.

Here is a sample json object:

{{
    "slides": [
        {{
            "background": {{
                "type": "image",
                "url": "https://cghemaaztqssvxbmmzwq.supabase.co/storage/v1/object/public/files/0.9467362248042711.jpg",
            }},
            "children": [
                {{
                    "type": "text",
                    "content": "Late Night Conversations",
                    "font": {{"color": "white", "size": 50, "style": "bold"}},
                    "position": {{"x": 50, "y": 50}},
                }}
            ],
            "duration": 5,
        }},
        {{
            "background": {{
                "type": "image",
                "url": "https://cghemaaztqssvxbmmzwq.supabase.co/storage/v1/object/public/files/0.29896717775346804.jpg",
            }},
            "children": [
                {{
                    "type": "text",
                    "content": "Exploring New Ideas",
                    "font": {{"color": "yellow", "size": 50, "style": "italic"}},
                    "position": {{"x": 50, "y": 50}},
                }}
            ],
            "duration": 5,
        }},
        {{
            "background": {{
                "type": "image",
                "url": "https://cghemaaztqssvxbmmzwq.supabase.co/storage/v1/object/public/files/0.4398063834249133.jpg",
            }},
            "children": [
                {{
                    "type": "text",
                    "content": "A Classroom Full of Dreams",
                    "font": {{"color": "white", "size": 50, "style": "bold"}},
                    "position": {{"x": 50, "y": 50}},
                }}
            ],
            "duration": 5,
        }},
        {{
            "background": {{"type": "color", "color": (0, 0, 0)}},  # Black background
            "children": [
                {{
                    "type": "text",
                    "content": "Memories Made, Lessons Learned!",
                    "font": {{"color": "white", "size": 50, "style": "bold"}},
                    "position": {{"x": 50, "y": 100}},
                }}
            ],
            "duration": 5,
        }},
    ],
    "output": "output_video.mp4",
    "background_music": "nights.mp3",
}}
    
Here is my trip details:
{trip_details}
"""
    )
    | chatOpenAI
)

MusicGenerationPrompt = (
    PromptTemplate.from_template(
        """
I have made a trip recently. I have some images from the trip. I want to make a video of the trip. I will provide you with the images and you will have to suggest me a music that vibes with the images and the trip. You will just provide me the name of a perfect music. The music must be released after 2015.

Output format:
<output>
    ... write the name of the music here ...
</output>

Here is my trip details:
{trip_details}
    
    """
    )
    | chatOpenAI
)

BlogGenerationPrompt = (
    PromptTemplate.from_template(
        """
I went on a trip and I took some photos. Here are some of the photos I took. Can you help me write a blog post about my trip? I will provide you with the photos and you will have to write a blog post about my trip. You will provide a Markdown formatted blog that is nicely presented. Include the images as URLs. You can use the descriptions of these images to write the blog. You can also use the date and time of the photos.

You must output the result in markdown format. Also, you must resize the images to 500px width.

Here are the photos I took:

{photos} 
    """
    )
    | chatOpenAI
)

TripPlanPrompt = (
    {
        "budget": itemgetter("budget"),
        "origin": itemgetter("origin"),
        "destination": itemgetter("destination"),
        "start_date": itemgetter("start_date"),
        "end_date": itemgetter("end_date"),
        "dest_lat": itemgetter("dest_lat"),
        "dest_lng": itemgetter("dest_lng"),
        "routes": itemgetter("routes"),
        "hotels": itemgetter("hotels"),
        "restaurants": itemgetter("restaurants"),
        "weather": itemgetter("weather"),
        "tourist_attraction": itemgetter("tourist_attraction"),
    }
    | ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a trip advisor. You have to plan a trip for a user. The user will provide you with the origin, destination, start date, and end date of the trip.
The user will also supply you with nearby hotels, restaurants, and weather forecast of the destination. You have to plan the trip for the user.

You will make a trip plan for the user. 
The user will ask you to plan a trip for them with different budgets like low, medium, high, luxury.
You will have to generate the trip according to their budget.

You will provide the user with the following sections:

- Title of the trip
Format:
<title>
... write the title of the trip here. this must be short and concise ...
</title>
- Summary of the trip.
Format:
<summary>
... write the summary here in markdown format ...
</summary>
- The routes from the origin to the destination. You can provide multiple routes if available. You can write this inside a table.
Format:
<routes>
... write the routes here in markdown format. you can add some icons here! your information shoould be very detailed. you should only provide routes using bus, train, or flight.. if you provide multiple routes, you should provide the cost and time of each route.
</routes>
- The list of hotels near the destination.
Format:
<hotels>
... write the list of hotels here in markdown format. include the cost and ratings if available. you can use some icons here too! also, you can add images of the hotels. also, you should resize the images to 200px width. include the room facilites, costing. also include contact information, website links, social links and booking links if available. your information shoould be very detailed ...
</hotels>
- The list of restaurants near the destination.
Format:
<restaurants>
... write the list of restaurants here in markdown format. include the cost and ratings if available. you can use some icons here too! also, you can add images of the restaurants. also, you should resize the images to 200px width. include the cuisines and some reviews. also inlcude contact information, website links, social links and booking links if available. your information shoould be very detailed ...
</restaurants>
- The weather forecast of the destination.
Format:
<weather>
... write the weather forecast here in markdown format. you can make it a table or a list with sun, cloud, thunder, rain etc icons ...
</weather>
- The tourist attractions near the destination.
Format:
<tourist_attractions>
... write the tourist attractions here in markdown format. you can provide the list of tourist attractions, cost of the attractions, time to visit, etc. in details ... 
</tourist_attractions>
- Daily Itinerary
Format:
<itinerary>
... write the daily itinerary or daywise planning here in markdown format. you can provide the daily activities, places to visit, time to visit, cost of the activities, etc. in details ...
</itinerary>
- Cost Estimation
Format:
<cost>
... write the cost estimation here in markdown format. you can provide the cost of the trip, cost of hotels, cost of restaurants, cost of transportation etc. in details. this should also include cost of daily itinerary ...    
</cost>
- Places needed to be marked on the map
Format:
<map>
... write full name of hotels, restaurants, tourist attactions and locations you received separated by comma here. include as many as you can that came from the user ...
</map>

The user will provide you the necessary information. You have to use the information to create the trip plan for the user. You must not provide any wrong information such as writing links like example.com, or providing wrong information about the hotels, restaurants, etc. This is serious business and you must provide the correct information.

If any image or url is missing, don't make up any information. Just leave it blank.

You must strictly follow the format provided above. You must provide detailed information in each section. You must provide the information in markdown format. You must resize the images to the specified width.

""",
            ),
            (
                "user",
                """
I am planning to make a trip. My budget is {budget}. I am planning to go from {origin} to {destination}. I will start my trip on {start_date} and end on {end_date}. I have the following data for you:

Origin: {origin}
Destination: {destination}
Start Date: {start_date}
End Date: {end_date}
Destination Latitude: {dest_lat}
Destination Longitude: {dest_lng}
Routes: {routes}
Hotels: {hotels}
Restaurants: {restaurants}
Weather: {weather}
                
                """,
            ),
        ]
    )
    | chatOpenAI
)

ImageToTextPrompt = (
    {
        "image_data": itemgetter("image_path") | RunnableLambda(image_to_base64),
        "caption": itemgetter("caption"),
    }
    | ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You will be given an image. You will have to generate a descriptive text based on the image. You should try to cover every details in the image. You should describe the foreground of the image and background of the image separately. But you should not start the sentence with "The foreground of the image is" or "The background of the image is". You should act natural and spontaneous.

The caption of the image given by the user: {caption}
You can use this caption in generating the description too if the caption is relevant to the image.

Output format:

<output>
    <foreground>
        foreground text goes here
    </foreground>
    <background>
        background text goes here
    </background>
</output>

         """,
            ),
            (
                "user",
                [
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/jpeg;base64,{image_data}"},
                    }
                ],
            ),
        ]
    )
    | chatOpenAI
)

JokePrompt = PromptTemplate.from_template("Tell me a joke about {text}") | chatOpenAI


prompts = {
    "default": DefaultPrompt,
    "image_to_text": ImageToTextPrompt,
    "joke": JokePrompt,
}
