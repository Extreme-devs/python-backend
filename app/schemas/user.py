from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone_number: str

    class Config:
        orm_mode = True
