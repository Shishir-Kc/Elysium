from AI.Cloud.Groq.groq_ai import Agent
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()
agent = Agent()

class User(BaseModel):
    chat:str

@router.post("/chat/Agent",tags=['chat with ai Agent'])
async def ai_response(user:User):
    response = await agent.chat(user_message=user.chat)
    return response


