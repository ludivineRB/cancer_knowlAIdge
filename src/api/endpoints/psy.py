from fastapi import APIRouter
from ..schemas.psy import UserMessage, PsychologistResponse
from ..utils.core_psy import create_psychologue_agent

router = APIRouter()

agent=create_psychologue_agent()

# @router.post("/psychologue", response_model=PsychologistResponse)
# async def talk_to_psychologist(payload: UserMessage):
#     """
#     Envoyer un message au psychologue virtuel et recevoir une réponse.
#     """
#     reply = agent.invoke({"input": payload.message},
#         {"configurable": {"session_id": "default"}})
#     return PsychologistResponse(response=reply.content)
agent = create_psychologue_agent()

@router.post("/psychologue", response_model=PsychologistResponse)
async def talk_to_psychologist(payload: UserMessage):
    reply = agent(payload.message)  # 🆕 Appel direct
    return PsychologistResponse(response=reply)
