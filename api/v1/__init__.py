from fastapi import APIRouter
from .server_status.server_health import router as server_healths
from .Hyper_status.hyper_stats import router as hyper_stats
from .email.email import router as send_email
from .Test_workers.workers_test import router as test_worker
from .ai.ai_chat import router as ai_router
from .websocket.laptop_price import router as live_router 

router = APIRouter(prefix="/v1")
router.include_router(server_healths)
router.include_router(hyper_stats)
router.include_router(send_email)
router.include_router(test_worker)
router.include_router(ai_router)
router.include_router(live_router)