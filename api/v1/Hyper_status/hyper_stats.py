from fastapi import APIRouter
from Tools.Hyper.hyper_health import hyper_server_status

router=APIRouter()

@router.get('/hyper/status/',tags=['is_Hyper_active'])
async def  hyper_status():
    return await hyper_server_status() 
