from core.supabase import upload_file
from core.langchain_prompts import (
    ImageToTextPrompt,
    BlogGenerationPrompt,
    VlogGenerationPrompt,
    MusicGenerationPrompt,
)
from core.langchain_init import openAIEmbeddings
from core.vector_db import qdrant_db
from .download_music import download_track
from .video_gen import generate_video
import time
import requests
import uuid
import json


def upload_embedding(text: str, payload: dict):
    embedding = openAIEmbeddings.embed_query(text)
    qdrant_db.insert(
        collection_name="image_descriptions", payload=payload, embedding=embedding
    )


def upload_image(caption: str, url: str, filename: str, user_id: int):
    file_ext = filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"

    response = requests.get(url)
    with open(file_name, "wb") as file:
        file.write(response.content)

    output = ImageToTextPrompt.invoke({"image_path": file_name, "caption": caption})

    foreground = output.content.split("<foreground>")[1].split("</foreground>")[0]
    background = output.content.split("<background>")[1].split("</background>")[0]

    total = foreground + "\n" + background

    payload = {
        "user_id": user_id,
        "filename": filename,
        "caption": caption,
        "url": url,
        "foreground": foreground,
        "background": background,
        "created_at": int(time.time()),
    }

    upload_embedding(foreground, payload)
    upload_embedding(background, payload)
    upload_embedding(caption, payload)

    return total


def bag_of_words_scoring(text: str, search_text: str):
    text = text.split(" ")
    search_text = search_text.split(" ")
    score = 0
    for word in search_text:
        if word in text:
            score += 1
    return score


def image_search(text: str, user_id: int):
    results = qdrant_db.search(
        collection_name="image_descriptions",
        query=text,
        limit=20,
        filter={"user_id": user_id},
    )
    urls = []
    for result in results:
        bow_score = bag_of_words_scoring(
            result.payload["foreground"] + result.payload["background"], text
        )
        if result.score < 0.3 and bow_score == 0:
            continue
        urls.append(result.payload["url"])
    urls = list(set(urls))
    return {"urls": urls}


def generate_vlog(start: int, end: int, user_id: int, authorization: str):
    print("Calling generate blog...")
    plans = requests.get(
        "http://172.28.31.70:3000/api/v1/plans",
        headers={"Authorization": authorization},
    )
    j = plans.json()

    results = qdrant_db.get_range(
        start, end, collection_name="image_descriptions", filter={"user_id": user_id}
    )
    data = "TRIP DETAILS in MARKDOWN\n\n"
    data += j[0]["data"]
    index = 1
    for result in results[0]:
        data += "Image " + str(index) + "\n"
        data += f"Caption: {result.payload['caption']}\n"
        formatted_time = time.strftime(
            "%I:%M %p, %d %B %Y", time.localtime(result.payload["created_at"])
        )
        data += f"Date & Time: {formatted_time}\n"
        data += f"Description: {result.payload['foreground'] + result.payload['background']}\n"
        data += f"URL: {result.payload['url']}\n\n"
        index += 1
    print(data)
    print("Generating vlog...")
    music_name = MusicGenerationPrompt.invoke({"trip_details": data}).content
    print(music_name)
    music_name = music_name.split("<output>")[1].split("</output>")[0]
    print("Downloading music...")
    download_track(music_name, "x.mp3")
    print("Generating video script...")
    x = VlogGenerationPrompt.invoke({"trip_details": data}).content
    print(x)
    if "```json" in x:
        x = x.split("```json")[1].split("```")[0]
    print("Generating video...")
    x = eval(x)
    x["background_music"] = "x.mp3"
    output_file = generate_video(x)
    print("Uploading video...")
    upload_file(output_file)
    return output_file


def generate_blog(start: int, end: int, user_id: int, authorization: str):
    print("Calling generate blog...")
    plans = requests.get(
        "http://172.28.31.70:3000/api/v1/plans",
        headers={"Authorization": authorization},
    )
    j = plans.json()
    results = qdrant_db.get_range(
        start, end, user_id, collection_name="image_descriptions"
    )
    data = "TRIP DETAILS in MARKDOWN\n\n"
    data += j[0]["data"]

    index = 1
    for result in results[0]:
        data += "Image " + str(index) + "\n"
        data += f"Caption: {result.payload['caption']}\n"
        formatted_time = time.strftime(
            "%I:%M %p, %d %B %Y", time.localtime(result.payload["created_at"])
        )
        data += f"Date & Time: {formatted_time}\n"
        data += f"Description: {result.payload['foreground'] + result.payload['background']}\n"
        data += f"URL: {result.payload['url']}\n\n"
        index += 1
    print(data)
    print("Generating blog...")
    x = BlogGenerationPrompt.invoke({"photos": data}).content
    print(x)
    if "```html" in x:
        x = x.split("```html")[1].replace("```", "")
    return x
