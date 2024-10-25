from pydantic import BaseModel, EmailStr
from typing import List, Optional


class ImageInfo(BaseModel):
    name: str
    url: str
    description: Optional[str] = ""


class ImageList(BaseModel):
    caption: str
    files: List[ImageInfo]

    class Config:
        orm_mode = True


class ImageSearch(BaseModel):
    text: str

    class Config:
        orm_mode = True


class ImageSearchResponse(BaseModel):
    urls: List[str]


class ImageSearchRequest(BaseModel):
    text: str
    user_id: int

    class Config:
        orm_mode = True

class BlogRequest(BaseModel):
    start: int
    end: int

    class Config:
        orm_mode = True
        
        
class BlogResponse(BaseModel):
    blog: str

    class Config:
        orm_mode = True


class VideoResponse(BaseModel):
    filename: str

    class Config:
        orm_mode = True        
        
class GetPlanReq(BaseModel):
    budget: str
    origin: str
    destination: str
    start_date: str
    end_date: str
    dest_lat: str
    dest_lng: str

    class Config:
        orm_mode = True