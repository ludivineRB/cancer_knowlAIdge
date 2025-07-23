from pydantic import BaseModel
from typing import List, Optional

class QuestionRequest(BaseModel):
    question: str
    language: Optional[str] = "fr"

class AnswerResponse(BaseModel):
    answer: str
    articles: List[str]
    agents: List[str]
