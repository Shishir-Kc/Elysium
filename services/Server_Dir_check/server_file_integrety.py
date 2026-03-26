import logging
from services.elysium_server.restart import restart_elysium
import os

logger = logging.getLogger("uvicorn.errors")


async def check_sys_dir():
    path_exists = True
    paths = ["Logs/Hyper", "Logs/Elysium"]
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            path_exists = False

    if not path_exists:
        logger.info("Created Logs Folder ")
        restart_elysium()

