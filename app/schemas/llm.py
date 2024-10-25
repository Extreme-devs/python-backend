from pydantic import BaseModel, EmailStr
from typing import Optional


class PromptOut(BaseModel):
    response: str

    class Config:
        orm_mode = True


class PromptIn(BaseModel):
    input_variables: dict
    template: Optional[str] = "default"