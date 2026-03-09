from fastapi import APIRouter

router = APIRouter()


@router.get("/health", name="server-health",tags=['Server_Health'])
async def server_health():
    return {"status": "ok"}
