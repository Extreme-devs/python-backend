from fastapi import APIRouter, HTTPException
from app.schemas.llm import PromptIn, PromptOut
from core.langchain_prompts import prompts

router = APIRouter()

@router.post("/", response_model=PromptOut)
async def prompt(prompt: PromptIn):
    input_variables = prompt.input_variables
    template = prompt.template
    try:
        response = prompts[template].invoke(input_variables)
        return {
            "response": response.content
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
