from fastapi import APIRouter, HTTPException
from app.schemas.vector_db import VectorCollections
from core.langchain_prompts import prompts
from core.vector_db import qdrant_db

router = APIRouter()

@router.get("/collections", response_model=VectorCollections)
async def prompt():
    collections = qdrant_db.get_collections()
    return collections
