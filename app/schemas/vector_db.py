from pydantic import BaseModel, EmailStr
from typing import Optional


class VectorCollections(BaseModel):
    collections: list
    
    class Config:
        orm_mode = True