from fastapi import APIRouter, HTTPException
from ..schemas.agents import QuestionRequest, AnswerResponse
from ..utils.services import process_question

router = APIRouter()

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(payload: QuestionRequest):
    try:
        result = await process_question(payload.question, payload.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
