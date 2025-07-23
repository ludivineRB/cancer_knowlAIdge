from pydantic import BaseModel

class UserMessage(BaseModel):
    """Schéma pour les messages envoyés par l'utilisateur."""
    session_id: str
    message: str


class PsychologistResponse(BaseModel):
    """Schéma pour les réponses générées par l'agent."""
    response: str
