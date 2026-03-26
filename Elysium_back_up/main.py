from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.v1 import router
from assets.Elysium.start_up import (
    wakey_wakey,
    sleppy_sleppy,
)
from services.Server_Dir_check.server_file_integrety import check_sys_dir


@asynccontextmanager
async def Lifespan(elysium_server: FastAPI):
    await check_sys_dir()
    await wakey_wakey()
    yield
    await sleppy_sleppy()


elysium_server = FastAPI(
    description="Home Server",
    title="Elysium",
    version="0.0.1",
    docs_url="/",
    lifespan=Lifespan,
)

elysium_server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)

f"""

 ↱ {elysium_server.include_router(router, prefix="/api")}
 This right here is for V1 api only ! 

    This runs the container ! -  > docker run -d -p 8000:8000 --env-file ../.env --name elysium_server elysium

    This stops and removes the container -> docker stop elysium_server && docker rm elysium_server
 
 """
