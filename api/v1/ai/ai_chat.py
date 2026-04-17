from AI.Cloud.Groq.groq_ai import Agent
from fastapi import APIRouter
from pydantic import BaseModel
import httpx
import os

router = APIRouter()
agent = Agent()


class User(BaseModel):
    chat: str
    thread_id: str | None = None


class ClearHistory(BaseModel):
    thread_id: str | None = None


class SetModelRequest(BaseModel):
    provider: str
    model_name: str


@router.post("/chat/Agent", tags=["chat with ai Agent"])
async def ai_response(user: User):
    response = await agent.chat(
        user_message=user.chat,
        thread_id=user.thread_id,
    )
    return response


@router.post("/chat/Agent/clear", tags=["chat with ai Agent"])
async def clear_chat_history(body: ClearHistory):
    agent.clear_history(thread_id=body.thread_id)
    return {"status": "history cleared"}


@router.get("/chat/Agent/history", tags=["chat with ai Agent"])
async def get_chat_history(thread_id: str | None = None):
    messages = agent.get_conversation_history(thread_id=thread_id)
    return [
        {
            "role": msg.__class__.__name__.replace("Message", "").lower(),
            "content": getattr(msg, "content", ""),
        }
        for msg in messages
        if getattr(msg, "content", None)
    ]


@router.get("/chat/models", tags=["chat with ai Agent"])
async def list_available_models():
    """Fetch models from Groq (Cloud) and Ollama (Local)."""
    models = {
        "current": {
            "provider": agent.provider,
            "model_name": agent.model_name
        },
        "providers": {
            "groq": [],
            "ollama": []
        }
    }
    
    # Fetch from Groq
    groq_api = os.getenv("GROQ_API")
    if groq_api:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    "https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {groq_api}"},
                    timeout=5.0
                )
                if r.status_code == 200:
                    data = r.json().get("data", [])
                    # Filter out models that aren't chat models if needed, 
                    # but for now we'll just list them all
                    models["providers"]["groq"] = [m["id"] for m in data]
        except Exception:
            pass

    # Fetch from Ollama (Local)
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("http://localhost:11434/api/tags", timeout=2.0)
            if r.status_code == 200:
                data = r.json().get("models", [])
                models["providers"]["ollama"] = [m["name"] for m in data]
    except Exception:
        pass

    return models


@router.post("/chat/model", tags=["chat with ai Agent"])
async def set_active_model(req: SetModelRequest):
    """Switch the active AI model."""
    try:
        agent.set_model(provider=req.provider, model_name=req.model_name)
        return {
            "status": "success",
            "provider": agent.provider,
            "model_name": agent.model_name
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
