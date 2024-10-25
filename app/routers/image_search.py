import time
from fastapi import APIRouter, HTTPException, Request
from app.schemas.image_search import (
    ImageList,
    ImageSearchRequest,
    ImageSearchResponse,
    BlogRequest,
    BlogResponse,
    GetPlanReq,
    VideoResponse,
)
from trip.generate_trip import plan_trip
from trip.image_search import upload_image, image_search, generate_blog, generate_vlog
from core.vector_db import qdrant_db
import requests
import jwt

router = APIRouter()


@router.post("/upload", response_model=ImageList)
async def prompt(req: ImageList, request: Request):
    token = request.headers.get("authorization")
    u = token.split(" ")[1]
    decoded_payload = jwt.decode(u, options={"verify_signature": False})
    user_id = decoded_payload["id"]
    print(req.dict())
    caption = req.caption
    files = req.files
    response = {"caption": caption, "files": []}
    try:
        for file in files:
            url = file.url
            name = file.name
            x = upload_image(caption=caption, url=url, filename=name, user_id=user_id)
            print(x)
            response["files"].append({"name": name, "url": url, "description": x})

        requests.post(
            "http://172.28.31.70:3000/api/v1/posts",
            json=response,
            headers={
                "Content-Type": "application/json",
                "Authorization": token,
            },
        )
        return response
    except Exception as e:
        print(str(e))
        return str(e)


@router.post("/search", response_model=ImageSearchResponse)
async def search(req: ImageSearchRequest):
    return image_search(req.text, req.user_id)


@router.post("/blog", response_model=BlogResponse)
async def generate_blogssss(req: BlogRequest, request: Request):
    # start = req.start
    # end = req.end
    headers = request.headers
    authorization = headers.get("authorization")
    token = authorization.split(" ")[1]

    decoded_payload = jwt.decode(token, options={"verify_signature": False})
    user_id = decoded_payload["id"]

    end = int(time.time())
    start = end - 24 * 3600 * 5

    return {"blog": generate_blog(start, end, user_id, authorization)}


@router.post("/vlog", response_model=VideoResponse)
async def generate_vlogss(request: Request):
    # start = req.start
    # end = req.end
    end = int(time.time())
    start = end - 24 * 3600 * 5

    headers = request.headers
    authorization = headers.get("authorization")
    token = authorization.split(" ")[1]

    decoded_payload = jwt.decode(token, options={"verify_signature": False})
    user_id = decoded_payload["id"]

    return {"filename": generate_vlog(start, end, user_id, authorization)}


@router.post("/get_plan")
async def get_plan(req: GetPlanReq):
    return plan_trip(
        req.origin,
        req.destination,
        req.start_date,
        req.end_date,
        req.dest_lat,
        req.dest_lng,
        req.budget,
    )
